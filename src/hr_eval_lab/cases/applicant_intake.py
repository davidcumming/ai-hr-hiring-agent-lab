"""Deterministic applicant and candidate-package intake over workflow storage."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Literal, cast

from hr_eval_lab.cases.service import HR_WORKFLOW_ROLE, RecruitmentCaseService
from hr_eval_lab.domain import ids
from hr_eval_lab.domain.schemas.audit import ActorContext
from hr_eval_lab.domain.schemas.cases import (
    ApplicantCreateRequest,
    ApplicantDetailResult,
    ApplicantImportRequest,
    ApplicantImportResult,
    ApplicantListResult,
    ApplicantRegistrationResult,
    ApplicantSetConfirmationResult,
    ApplicantSetConfirmRequest,
    ApplicantSummary,
    CandidateDocumentRegisterRequest,
    CandidateDocumentRegistrationResult,
    CandidateDocumentSummary,
    CandidatePackageSummary,
    CaseNextAction,
    ImportFinding,
    ImportFindingsResult,
)
from hr_eval_lab.domain.schemas.workflow import (
    Applicant,
    CandidatePackage,
    CaseEvent,
    CaseTask,
    RecruitmentCase,
    SourceDocument,
    WorkflowGate,
)
from hr_eval_lab.domain.schemas.workflow_artifacts import (
    candidate_document_raw_path,
    candidate_package_path,
)
from hr_eval_lab.persistence.workflow_storage import WorkflowStorageBackend

PACKAGE_VERSION = "v1"
PENDING_APPLICANT_SET_VERSION = "pending"
MAX_ACTIVE_APPLICANTS = 5
ALLOWED_DOCUMENT_TYPES = {"resume", "cover_letter", "other_candidate_source"}
REQUIRED_DOCUMENT_TYPE = "resume"
APPLICANT_SET_GATE_ID = "applicant_set_confirmation_required"
APPLICANT_SET_GATE_ROW_KEY = f"gate#{APPLICANT_SET_GATE_ID}"
ASSESSMENT_GATE_ROW_KEY = "gate#assessment_unlocked"
CONFIRM_TASK_ROW_KEY = "task#confirm_applicant_set"
RESOLVE_FINDINGS_TASK_ROW_KEY = "task#resolve_import_findings"

ApplicantIntakeError = Literal[
    "unknown_case_id",
    "unknown_candidate_id",
    "duplicate_candidate_ref",
    "candidate_limit_exceeded",
    "unsupported_document_type",
    "applicant_set_incomplete",
    "applicant_set_already_confirmed",
    "applicant_set_locked",
]
ApplicantIntakeResult = (
    ApplicantRegistrationResult
    | ApplicantListResult
    | ApplicantDetailResult
    | CandidateDocumentRegistrationResult
    | ApplicantImportResult
    | ImportFindingsResult
    | ApplicantSetConfirmationResult
)


@dataclass(frozen=True)
class ApplicantIntakeSnapshot:
    case_id: str | None = None
    correlation_id: str | None = None
    result: ApplicantIntakeResult | None = None
    next_actions: list[CaseNextAction] = field(default_factory=list)
    error: ApplicantIntakeError | None = None
    blocked: bool = False
    safe_details: str | None = None


@dataclass(frozen=True)
class _PackageAssembly:
    applicant: Applicant
    package: CandidatePackage
    findings: list[ImportFinding]


class ApplicantIntakeService:
    """Applicant/package intake logic over ``WorkflowStorageBackend`` only."""

    def __init__(
        self,
        storage: WorkflowStorageBackend,
        *,
        candidate_id_fn: Callable[[], str] = ids.new_candidate_id,
        document_id_fn: Callable[[], str] = ids.new_document_id,
        event_id_fn: Callable[[], str] = ids.new_event_id,
        now_fn: Callable[[], str] = ids.utc_now_iso,
    ) -> None:
        self._storage = storage
        self._candidate_id_fn = candidate_id_fn
        self._document_id_fn = document_id_fn
        self._event_id_fn = event_id_fn
        self._now_fn = now_fn

    def register_applicant(
        self,
        case_id: str,
        request: ApplicantCreateRequest,
        actor: ActorContext,
    ) -> ApplicantIntakeSnapshot:
        case = self._get_case(case_id)
        if case is None:
            return ApplicantIntakeSnapshot(error="unknown_case_id")
        locked = self._locked_snapshot(case)
        if locked is not None:
            return locked

        duplicate = self._first_duplicate_ref(
            self._list_active_applicants(case_id),
            [request.candidate_ref],
        )
        if duplicate is not None:
            return ApplicantIntakeSnapshot(
                case_id=case_id,
                correlation_id=case.correlation_id,
                error="duplicate_candidate_ref",
                safe_details=f"duplicate candidate_ref '{duplicate}'",
            )
        if len(self._list_active_applicants(case_id)) >= MAX_ACTIVE_APPLICANTS:
            return ApplicantIntakeSnapshot(
                case_id=case_id,
                correlation_id=case.correlation_id,
                error="candidate_limit_exceeded",
                safe_details="active applicant cap is five candidates",
            )

        created_at = self._now_fn()
        event_id = self._event_id_fn()
        applicant = self._new_applicant(
            case=case,
            request=ApplicantCreateRequest(
                synthetic=True,
                candidate_ref=request.candidate_ref,
                display_label=request.display_label,
            ),
            actor=actor,
            created_at=created_at,
        )
        assembly = self._write_candidate_package(
            case=case,
            applicant=applicant,
            documents=[],
            actor=actor,
            updated_at=created_at,
        )
        self._storage.upsert_table_entity(assembly.applicant)
        self._storage.upsert_table_entity(assembly.package)
        self._storage.upsert_table_entity(
            self._event(
                case=case,
                actor=actor,
                event_id=event_id,
                created_at=created_at,
                event_type="applicant_registered",
                summary="Applicant registered for candidate-package intake.",
                candidate_id=assembly.applicant.candidate_id,
                safe_details={
                    "candidate_id": assembly.applicant.candidate_id,
                    "candidate_ref": assembly.applicant.candidate_ref,
                    "package_version": assembly.package.package_version,
                    "package_status": assembly.package.package_status,
                    "finding_count": len(assembly.findings),
                    "synthetic": True,
                },
            )
        )
        self._refresh_applicant_state(
            case=case,
            actor=actor,
            updated_at=created_at,
        )

        snapshot = self._case_snapshot(case_id)
        if snapshot is None:  # pragma: no cover - defensive storage invariant
            raise RuntimeError(f"case {case_id!r} disappeared during applicant intake")
        return ApplicantIntakeSnapshot(
            case_id=case_id,
            correlation_id=case.correlation_id,
            result=ApplicantRegistrationResult(
                case=snapshot.result.case,
                applicant=self._applicant_summary(assembly.applicant),
                package=self._package_summary(assembly.package),
                findings=assembly.findings,
            ),
            next_actions=snapshot.result.next_actions,
        )

    def list_applicants(self, case_id: str) -> ApplicantIntakeSnapshot:
        case = self._get_case(case_id)
        if case is None:
            return ApplicantIntakeSnapshot(error="unknown_case_id")
        applicants = self._list_active_applicants(case_id)
        packages = self._list_packages(case_id)
        findings = self._compute_findings(case_id, applicants)
        snapshot = self._case_snapshot(case_id)
        if snapshot is None:  # pragma: no cover - defensive storage invariant
            raise RuntimeError(f"case {case_id!r} was readable but snapshot failed")
        return ApplicantIntakeSnapshot(
            case_id=case_id,
            correlation_id=case.correlation_id,
            result=ApplicantListResult(
                case_id=case_id,
                applicants=[self._applicant_summary(applicant) for applicant in applicants],
                packages=[self._package_summary(package) for package in packages],
                findings=findings,
                can_confirm=self._can_confirm(applicants, packages, findings),
            ),
            next_actions=snapshot.result.next_actions,
        )

    def get_applicant(self, case_id: str, candidate_id: str) -> ApplicantIntakeSnapshot:
        case = self._get_case(case_id)
        if case is None:
            return ApplicantIntakeSnapshot(error="unknown_case_id")
        applicant = self._get_applicant(case_id, candidate_id)
        if applicant is None:
            return ApplicantIntakeSnapshot(
                case_id=case_id,
                correlation_id=case.correlation_id,
                error="unknown_candidate_id",
            )
        documents = self._list_candidate_documents(case_id, candidate_id)
        package = self._get_package(case_id, candidate_id)
        findings = self._findings_for_candidate(applicant, documents)
        snapshot = self._case_snapshot(case_id)
        if snapshot is None:  # pragma: no cover - defensive storage invariant
            raise RuntimeError(f"case {case_id!r} was readable but snapshot failed")
        return ApplicantIntakeSnapshot(
            case_id=case_id,
            correlation_id=case.correlation_id,
            result=ApplicantDetailResult(
                case_id=case_id,
                applicant=self._applicant_summary(applicant),
                documents=[self._document_summary(document) for document in documents],
                package=self._package_summary(package) if package is not None else None,
                findings=findings,
            ),
            next_actions=snapshot.result.next_actions,
        )

    def register_candidate_document(
        self,
        case_id: str,
        candidate_id: str,
        request: CandidateDocumentRegisterRequest,
        actor: ActorContext,
    ) -> ApplicantIntakeSnapshot:
        case = self._get_case(case_id)
        if case is None:
            return ApplicantIntakeSnapshot(error="unknown_case_id")
        locked = self._locked_snapshot(case)
        if locked is not None:
            return locked
        applicant = self._get_applicant(case_id, candidate_id)
        if applicant is None:
            return ApplicantIntakeSnapshot(
                case_id=case_id,
                correlation_id=case.correlation_id,
                error="unknown_candidate_id",
            )
        document_type = request.document_type.strip().casefold()
        if document_type not in ALLOWED_DOCUMENT_TYPES:
            return ApplicantIntakeSnapshot(
                case_id=case_id,
                correlation_id=case.correlation_id,
                error="unsupported_document_type",
                safe_details=f"unsupported document_type '{request.document_type}'",
            )

        created_at = self._now_fn()
        event_id = self._event_id_fn()
        document_id = self._document_id_fn()
        raw_path = candidate_document_raw_path(case_id, candidate_id, document_id)
        raw_ref = self._storage.write_blob_artifact(
            raw_path,
            request.content_text.encode("utf-8"),
        )
        document = SourceDocument(
            PartitionKey=case_id,
            RowKey=f"doc#{document_id}",
            created_at=created_at,
            created_by_actor_id=actor.actor_id,
            created_by_role=HR_WORKFLOW_ROLE,
            correlation_id=case.correlation_id,
            case_id=case_id,
            document_id=document_id,
            candidate_id=candidate_id,
            document_type=document_type,
            source_label=request.source_label,
            source_origin=request.source_origin,
            blob_path=raw_ref.blob_path,
            mime_type=request.mime_type,
            file_name=request.file_name,
            size_bytes=raw_ref.size_bytes,
            sha256=raw_ref.sha256,
            processing_status="registered",
            version=PACKAGE_VERSION,
            synthetic=True,
        )
        documents = self._list_candidate_documents(case_id, candidate_id) + [document]
        assembly = self._write_candidate_package(
            case=case,
            applicant=applicant,
            documents=documents,
            actor=actor,
            updated_at=created_at,
        )
        self._storage.upsert_table_entity(document)
        self._storage.upsert_table_entity(assembly.package)
        self._storage.upsert_table_entity(assembly.applicant)
        self._storage.upsert_table_entity(
            self._event(
                case=case,
                actor=actor,
                event_id=event_id,
                created_at=created_at,
                event_type="candidate_document_registered",
                summary="Candidate document registered and package metadata refreshed.",
                candidate_id=candidate_id,
                artifact_id=document_id,
                artifact_version=PACKAGE_VERSION,
                safe_details={
                    "candidate_id": candidate_id,
                    "candidate_ref": applicant.candidate_ref,
                    "document_id": document_id,
                    "document_type": document_type,
                    "source_origin": request.source_origin,
                    "source_label": request.source_label,
                    "file_name": request.file_name,
                    "mime_type": request.mime_type,
                    "blob_path": raw_ref.blob_path,
                    "sha256": raw_ref.sha256,
                    "size_bytes": raw_ref.size_bytes,
                    "package_status": assembly.package.package_status,
                    "synthetic": True,
                },
            )
        )
        self._refresh_applicant_state(
            case=case,
            actor=actor,
            updated_at=created_at,
        )

        snapshot = self._case_snapshot(case_id)
        if snapshot is None:  # pragma: no cover - defensive storage invariant
            raise RuntimeError(f"case {case_id!r} disappeared during document intake")
        return ApplicantIntakeSnapshot(
            case_id=case_id,
            correlation_id=case.correlation_id,
            result=CandidateDocumentRegistrationResult(
                case=snapshot.result.case,
                applicant=self._applicant_summary(assembly.applicant),
                document=self._document_summary(document),
                package=self._package_summary(assembly.package),
                findings=assembly.findings,
            ),
            next_actions=snapshot.result.next_actions,
        )

    def process_import(
        self,
        case_id: str,
        request: ApplicantImportRequest,
        actor: ActorContext,
    ) -> ApplicantIntakeSnapshot:
        case = self._get_case(case_id)
        if case is None:
            return ApplicantIntakeSnapshot(error="unknown_case_id")
        locked = self._locked_snapshot(case)
        if locked is not None:
            return locked

        active_applicants = self._list_active_applicants(case_id)
        refs = [candidate.candidate_ref for candidate in request.candidates]
        duplicate = self._first_duplicate_ref(active_applicants, refs)
        if duplicate is not None:
            return ApplicantIntakeSnapshot(
                case_id=case_id,
                correlation_id=case.correlation_id,
                error="duplicate_candidate_ref",
                safe_details=f"duplicate candidate_ref '{duplicate}'",
            )
        if len(active_applicants) + len(request.candidates) > MAX_ACTIVE_APPLICANTS:
            return ApplicantIntakeSnapshot(
                case_id=case_id,
                correlation_id=case.correlation_id,
                error="candidate_limit_exceeded",
                safe_details="active applicant cap is five candidates",
            )
        unsupported = self._first_unsupported_document_type(request)
        if unsupported is not None:
            return ApplicantIntakeSnapshot(
                case_id=case_id,
                correlation_id=case.correlation_id,
                error="unsupported_document_type",
                safe_details=f"unsupported document_type '{unsupported}'",
            )

        created_at = self._now_fn()
        event_id = self._event_id_fn()
        imported_applicants: list[Applicant] = []
        imported_packages: list[CandidatePackage] = []
        document_count = 0
        for candidate in request.candidates:
            applicant = self._new_applicant(
                case=case,
                request=ApplicantCreateRequest(
                    synthetic=True,
                    candidate_ref=candidate.candidate_ref,
                    display_label=candidate.display_label,
                ),
                actor=actor,
                created_at=created_at,
            )
            documents: list[SourceDocument] = []
            for document_request in candidate.documents:
                document_id = self._document_id_fn()
                document_type = document_request.document_type.strip().casefold()
                raw_ref = self._storage.write_blob_artifact(
                    candidate_document_raw_path(
                        case_id,
                        applicant.candidate_id,
                        document_id,
                    ),
                    document_request.content_text.encode("utf-8"),
                )
                documents.append(
                    SourceDocument(
                        PartitionKey=case_id,
                        RowKey=f"doc#{document_id}",
                        created_at=created_at,
                        created_by_actor_id=actor.actor_id,
                        created_by_role=HR_WORKFLOW_ROLE,
                        correlation_id=case.correlation_id,
                        case_id=case_id,
                        document_id=document_id,
                        candidate_id=applicant.candidate_id,
                        document_type=document_type,
                        source_label=document_request.source_label,
                        source_origin=document_request.source_origin,
                        blob_path=raw_ref.blob_path,
                        mime_type=document_request.mime_type,
                        file_name=document_request.file_name,
                        size_bytes=raw_ref.size_bytes,
                        sha256=raw_ref.sha256,
                        processing_status="registered",
                        version=PACKAGE_VERSION,
                        synthetic=True,
                    )
                )
            assembly = self._write_candidate_package(
                case=case,
                applicant=applicant,
                documents=documents,
                actor=actor,
                updated_at=created_at,
            )
            self._storage.upsert_table_entity(assembly.applicant)
            for document in documents:
                self._storage.upsert_table_entity(document)
            self._storage.upsert_table_entity(assembly.package)
            imported_applicants.append(assembly.applicant)
            imported_packages.append(assembly.package)
            document_count += len(documents)

        self._storage.upsert_table_entity(
            self._event(
                case=case,
                actor=actor,
                event_id=event_id,
                created_at=created_at,
                event_type="applicant_import_processed",
                summary="Applicant import processed for candidate-package intake.",
                safe_details={
                    "candidate_ids": [
                        applicant.candidate_id for applicant in imported_applicants
                    ],
                    "candidate_refs": [
                        applicant.candidate_ref for applicant in imported_applicants
                    ],
                    "imported_count": len(imported_applicants),
                    "document_count": document_count,
                    "synthetic": True,
                },
            )
        )
        self._refresh_applicant_state(
            case=case,
            actor=actor,
            updated_at=created_at,
        )

        applicants = self._list_active_applicants(case_id)
        packages = self._list_packages(case_id)
        findings = self._compute_findings(case_id, applicants)
        snapshot = self._case_snapshot(case_id)
        if snapshot is None:  # pragma: no cover - defensive storage invariant
            raise RuntimeError(f"case {case_id!r} disappeared during applicant import")
        return ApplicantIntakeSnapshot(
            case_id=case_id,
            correlation_id=case.correlation_id,
            result=ApplicantImportResult(
                case=snapshot.result.case,
                applicants=[
                    self._applicant_summary(applicant) for applicant in imported_applicants
                ],
                packages=[
                    self._package_summary(package) for package in imported_packages
                ],
                findings=findings,
                imported_count=len(imported_applicants),
                document_count=document_count,
                can_confirm=self._can_confirm(applicants, packages, findings),
            ),
            next_actions=snapshot.result.next_actions,
        )

    def get_import_findings(self, case_id: str) -> ApplicantIntakeSnapshot:
        case = self._get_case(case_id)
        if case is None:
            return ApplicantIntakeSnapshot(error="unknown_case_id")
        applicants = self._list_active_applicants(case_id)
        packages = self._list_packages(case_id)
        findings = self._compute_findings(case_id, applicants)
        snapshot = self._case_snapshot(case_id)
        if snapshot is None:  # pragma: no cover - defensive storage invariant
            raise RuntimeError(f"case {case_id!r} was readable but snapshot failed")
        return ApplicantIntakeSnapshot(
            case_id=case_id,
            correlation_id=case.correlation_id,
            result=ImportFindingsResult(
                case_id=case_id,
                findings=findings,
                packages=[self._package_summary(package) for package in packages],
                can_confirm=self._can_confirm(applicants, packages, findings),
            ),
            next_actions=snapshot.result.next_actions,
        )

    def confirm_applicant_set(
        self,
        case_id: str,
        request: ApplicantSetConfirmRequest,
        actor: ActorContext,
    ) -> ApplicantIntakeSnapshot:
        case = self._get_case(case_id)
        if case is None:
            return ApplicantIntakeSnapshot(error="unknown_case_id")
        if case.applicant_set_version is not None:
            return ApplicantIntakeSnapshot(
                case_id=case_id,
                correlation_id=case.correlation_id,
                error="applicant_set_already_confirmed",
                safe_details=f"applicant_set_version '{case.applicant_set_version}' is already confirmed",
            )

        applicants = self._list_active_applicants(case_id)
        packages = self._list_packages(case_id)
        findings = self._compute_findings(case_id, applicants)
        if not self._can_confirm(applicants, packages, findings):
            snapshot = self._case_snapshot(case_id)
            return ApplicantIntakeSnapshot(
                case_id=case_id,
                correlation_id=case.correlation_id,
                result=ImportFindingsResult(
                    case_id=case_id,
                    findings=findings,
                    packages=[self._package_summary(package) for package in packages],
                    can_confirm=False,
                ),
                next_actions=snapshot.result.next_actions if snapshot else [],
                error="applicant_set_incomplete",
                blocked=True,
                safe_details="at least one complete candidate package is required and all active applicant packages must be complete",
            )

        updated_at = self._now_fn()
        event_id = self._event_id_fn()
        confirmed_ids: list[str] = []
        for applicant in applicants:
            confirmed_ids.append(applicant.candidate_id)
            self._storage.upsert_table_entity(
                applicant.model_copy(
                    update={
                        "import_status": "confirmed",
                        "applicant_set_version": request.applicant_set_version,
                        "blocking_findings": [],
                        "updated_at": updated_at,
                        "updated_by_actor_id": actor.actor_id,
                        "updated_by_role": HR_WORKFLOW_ROLE,
                    }
                )
            )

        self._storage.upsert_table_entity(
            self._event(
                case=case,
                actor=actor,
                event_id=event_id,
                created_at=updated_at,
                event_type="applicant_set_confirmed",
                summary="Applicant set confirmed for later assessment readiness.",
                safe_details={
                    "candidate_ids": confirmed_ids,
                    "applicant_set_version": request.applicant_set_version,
                    "package_version": PACKAGE_VERSION,
                    "assessment_unlocked": "locked",
                    "synthetic": True,
                },
            )
        )
        self._complete_applicant_set_confirmation(
            case=case,
            actor=actor,
            updated_at=updated_at,
            event_id=event_id,
            applicant_set_version=request.applicant_set_version,
        )

        snapshot = self._case_snapshot(case_id)
        if snapshot is None:  # pragma: no cover - defensive storage invariant
            raise RuntimeError(f"case {case_id!r} disappeared during confirmation")
        return ApplicantIntakeSnapshot(
            case_id=case_id,
            correlation_id=case.correlation_id,
            result=ApplicantSetConfirmationResult(
                case=snapshot.result.case,
                confirmed_applicant_set_version=request.applicant_set_version,
                confirmed_candidate_ids=confirmed_ids,
                packages=[self._package_summary(package) for package in packages],
                assessment_unlocked="locked",
            ),
            next_actions=snapshot.result.next_actions,
        )

    def _get_case(self, case_id: str) -> RecruitmentCase | None:
        return cast(
            RecruitmentCase | None,
            self._storage.get_table_entity(RecruitmentCase, case_id, "case"),
        )

    def _locked_snapshot(self, case: RecruitmentCase) -> ApplicantIntakeSnapshot | None:
        if case.applicant_set_version is None:
            return None
        return ApplicantIntakeSnapshot(
            case_id=case.case_id,
            correlation_id=case.correlation_id,
            error="applicant_set_locked",
            safe_details=(
                "confirmed_applicant_set_version="
                f"'{case.applicant_set_version}'"
            ),
        )

    def _case_snapshot(self, case_id: str):
        return RecruitmentCaseService(self._storage).get_case(case_id)

    def _get_applicant(self, case_id: str, candidate_id: str) -> Applicant | None:
        return cast(
            Applicant | None,
            self._storage.get_table_entity(
                Applicant,
                case_id,
                f"candidate#{candidate_id}",
            ),
        )

    def _get_package(self, case_id: str, candidate_id: str) -> CandidatePackage | None:
        return cast(
            CandidatePackage | None,
            self._storage.get_table_entity(
                CandidatePackage,
                case_id,
                f"package#{candidate_id}#{PACKAGE_VERSION}",
            ),
        )

    def _list_active_applicants(self, case_id: str) -> list[Applicant]:
        return [
            cast(Applicant, row)
            for row in sorted(
                self._storage.list_table_entities(Applicant, partition_key=case_id),
                key=lambda row: row.RowKey,
            )
            if cast(Applicant, row).import_status != "excluded"
        ]

    def _list_packages(self, case_id: str) -> list[CandidatePackage]:
        return [
            cast(CandidatePackage, row)
            for row in sorted(
                self._storage.list_table_entities(CandidatePackage, partition_key=case_id),
                key=lambda row: row.RowKey,
            )
        ]

    def _list_candidate_documents(
        self,
        case_id: str,
        candidate_id: str,
    ) -> list[SourceDocument]:
        return [
            cast(SourceDocument, row)
            for row in sorted(
                self._storage.list_table_entities(SourceDocument, partition_key=case_id),
                key=lambda row: row.RowKey,
            )
            if cast(SourceDocument, row).candidate_id == candidate_id
            and cast(SourceDocument, row).processing_status != "excluded"
        ]

    def _new_applicant(
        self,
        *,
        case: RecruitmentCase,
        request: ApplicantCreateRequest,
        actor: ActorContext,
        created_at: str,
    ) -> Applicant:
        candidate_id = self._candidate_id_fn()
        return Applicant(
            PartitionKey=case.case_id,
            RowKey=f"candidate#{candidate_id}",
            created_at=created_at,
            created_by_actor_id=actor.actor_id,
            created_by_role=HR_WORKFLOW_ROLE,
            correlation_id=case.correlation_id,
            case_id=case.case_id,
            candidate_id=candidate_id,
            candidate_ref=request.candidate_ref,
            display_label=request.display_label or request.candidate_ref,
            import_status="incomplete",
            applicant_set_version=PENDING_APPLICANT_SET_VERSION,
            blocking_findings=[],
            synthetic=True,
        )

    def _write_candidate_package(
        self,
        *,
        case: RecruitmentCase,
        applicant: Applicant,
        documents: list[SourceDocument],
        actor: ActorContext,
        updated_at: str,
    ) -> _PackageAssembly:
        findings = self._findings_for_candidate(applicant, documents)
        blocking_findings = [
            finding.finding_type for finding in findings if finding.severity == "blocking"
        ]
        package_status = "blocked" if blocking_findings else "complete"
        required_status = {
            REQUIRED_DOCUMENT_TYPE: (
                "present"
                if any(document.document_type == REQUIRED_DOCUMENT_TYPE for document in documents)
                else "missing"
            ),
            "cover_letter": (
                "present"
                if any(document.document_type == "cover_letter" for document in documents)
                else "optional_missing"
            ),
        }
        document_ids = [document.document_id for document in documents]
        blob_path = candidate_package_path(
            case.case_id,
            applicant.candidate_id,
            PACKAGE_VERSION,
        )
        payload = {
            "artifact_type": "candidate_package",
            "case_id": case.case_id,
            "candidate_id": applicant.candidate_id,
            "candidate_ref": applicant.candidate_ref,
            "display_label": applicant.display_label,
            "package_version": PACKAGE_VERSION,
            "rubric_version": case.active_rubric_version or "unassigned",
            "document_ids": document_ids,
            "required_document_status": required_status,
            "package_status": package_status,
            "documents": [self._safe_document_ref(document) for document in documents],
            "findings": [finding.model_dump(mode="json") for finding in findings],
            "updated_at": updated_at,
            "updated_by_actor_id": actor.actor_id,
            "updated_by_role": HR_WORKFLOW_ROLE,
            "synthetic": True,
        }
        blob_ref = self._storage.write_blob_artifact(blob_path, payload)
        package = CandidatePackage(
            PartitionKey=case.case_id,
            RowKey=f"package#{applicant.candidate_id}#{PACKAGE_VERSION}",
            created_at=applicant.created_at,
            updated_at=updated_at,
            created_by_actor_id=applicant.created_by_actor_id,
            created_by_role=HR_WORKFLOW_ROLE,
            updated_by_actor_id=actor.actor_id,
            updated_by_role=HR_WORKFLOW_ROLE,
            correlation_id=case.correlation_id,
            case_id=case.case_id,
            candidate_id=applicant.candidate_id,
            package_version=PACKAGE_VERSION,
            rubric_version=case.active_rubric_version or "unassigned",
            document_ids=document_ids,
            required_document_status=required_status,
            package_status=package_status,
            blob_path=blob_ref.blob_path,
            sha256=blob_ref.sha256,
            synthetic=True,
        )
        updated_applicant = applicant.model_copy(
            update={
                "import_status": "imported" if package_status == "complete" else "incomplete",
                "blocking_findings": blocking_findings,
                "updated_at": updated_at,
                "updated_by_actor_id": actor.actor_id,
                "updated_by_role": HR_WORKFLOW_ROLE,
            }
        )
        return _PackageAssembly(
            applicant=updated_applicant,
            package=package,
            findings=findings,
        )

    def _refresh_applicant_state(
        self,
        *,
        case: RecruitmentCase,
        actor: ActorContext,
        updated_at: str,
    ) -> None:
        applicants = self._list_active_applicants(case.case_id)
        packages = self._list_packages(case.case_id)
        findings = self._compute_findings(case.case_id, applicants)
        can_confirm = self._can_confirm(applicants, packages, findings)
        blocking_findings = [
            finding for finding in findings if finding.severity == "blocking"
        ]
        self._ensure_confirm_task(
            case=case,
            actor=actor,
            updated_at=updated_at,
            can_confirm=can_confirm,
        )
        self._ensure_resolve_findings_task(
            case=case,
            actor=actor,
            updated_at=updated_at,
            blocking_findings=blocking_findings,
        )
        self._update_applicant_gate(
            case=case,
            actor=actor,
            updated_at=updated_at,
            findings=blocking_findings,
        )
        self._storage.upsert_table_entity(
            case.model_copy(
                update={
                    "case_status": "applicants_pending",
                    "current_stage": "stage_5_applicant_import",
                    "current_gate": APPLICANT_SET_GATE_ID,
                    "updated_at": updated_at,
                    "updated_by_actor_id": actor.actor_id,
                    "updated_by_role": HR_WORKFLOW_ROLE,
                }
            )
        )

    def _ensure_confirm_task(
        self,
        *,
        case: RecruitmentCase,
        actor: ActorContext,
        updated_at: str,
        can_confirm: bool,
    ) -> None:
        task = cast(
            CaseTask | None,
            self._storage.get_table_entity(CaseTask, case.case_id, CONFIRM_TASK_ROW_KEY),
        )
        if task is not None and task.status == "completed":
            return
        status = "open" if can_confirm else "blocked"
        updates = {
            "status": status,
            "assigned_actor_id": case.hr_owner_actor_id,
            "updated_at": updated_at,
            "updated_by_actor_id": actor.actor_id,
            "updated_by_role": HR_WORKFLOW_ROLE,
        }
        if task is None:
            task = CaseTask(
                PartitionKey=case.case_id,
                RowKey=CONFIRM_TASK_ROW_KEY,
                created_at=updated_at,
                created_by_actor_id=actor.actor_id,
                created_by_role=HR_WORKFLOW_ROLE,
                correlation_id=case.correlation_id,
                case_id=case.case_id,
                task_id="confirm_applicant_set",
                task_type="confirm_applicant_set",
                assigned_role=HR_WORKFLOW_ROLE,
                assigned_actor_id=case.hr_owner_actor_id,
                status=status,
                blocking_gate=APPLICANT_SET_GATE_ID,
                synthetic=True,
            )
        else:
            task = task.model_copy(update=updates)
        if task.status != "completed":
            self._storage.upsert_table_entity(task)

    def _ensure_resolve_findings_task(
        self,
        *,
        case: RecruitmentCase,
        actor: ActorContext,
        updated_at: str,
        blocking_findings: list[ImportFinding],
    ) -> None:
        task = cast(
            CaseTask | None,
            self._storage.get_table_entity(
                CaseTask,
                case.case_id,
                RESOLVE_FINDINGS_TASK_ROW_KEY,
            ),
        )
        status = "open" if blocking_findings else "completed"
        if task is None:
            task = CaseTask(
                PartitionKey=case.case_id,
                RowKey=RESOLVE_FINDINGS_TASK_ROW_KEY,
                created_at=updated_at,
                created_by_actor_id=actor.actor_id,
                created_by_role=HR_WORKFLOW_ROLE,
                correlation_id=case.correlation_id,
                case_id=case.case_id,
                task_id="resolve_import_findings",
                task_type="resolve_import_findings",
                assigned_role=HR_WORKFLOW_ROLE,
                assigned_actor_id=case.hr_owner_actor_id,
                status=status,
                blocking_gate=APPLICANT_SET_GATE_ID if blocking_findings else None,
                synthetic=True,
            )
        else:
            task = task.model_copy(
                update={
                    "status": status,
                    "blocking_gate": APPLICANT_SET_GATE_ID if blocking_findings else None,
                    "updated_at": updated_at,
                    "updated_by_actor_id": actor.actor_id,
                    "updated_by_role": HR_WORKFLOW_ROLE,
                }
            )
        self._storage.upsert_table_entity(task)

    def _update_applicant_gate(
        self,
        *,
        case: RecruitmentCase,
        actor: ActorContext,
        updated_at: str,
        findings: list[ImportFinding],
    ) -> None:
        gate = cast(
            WorkflowGate | None,
            self._storage.get_table_entity(
                WorkflowGate,
                case.case_id,
                APPLICANT_SET_GATE_ROW_KEY,
            ),
        )
        if gate is None or gate.gate_status in {"satisfied", "waived"}:
            return
        blocking_reasons = (
            [finding.message for finding in findings]
            if findings
            else ["Applicant set has not been confirmed."]
        )
        self._storage.upsert_table_entity(
            gate.model_copy(
                update={
                    "gate_status": "blocked",
                    "blocking_reasons": blocking_reasons,
                    "last_checked_at": updated_at,
                    "updated_at": updated_at,
                    "updated_by_actor_id": actor.actor_id,
                    "updated_by_role": HR_WORKFLOW_ROLE,
                }
            )
        )

    def _complete_applicant_set_confirmation(
        self,
        *,
        case: RecruitmentCase,
        actor: ActorContext,
        updated_at: str,
        event_id: str,
        applicant_set_version: str,
    ) -> None:
        confirm_task = cast(
            CaseTask | None,
            self._storage.get_table_entity(CaseTask, case.case_id, CONFIRM_TASK_ROW_KEY),
        )
        if confirm_task is not None:
            self._storage.upsert_table_entity(
                confirm_task.model_copy(
                    update={
                        "status": "completed",
                        "updated_at": updated_at,
                        "updated_by_actor_id": actor.actor_id,
                        "updated_by_role": HR_WORKFLOW_ROLE,
                        "completion_event_id": event_id,
                    }
                )
            )

        resolve_task = cast(
            CaseTask | None,
            self._storage.get_table_entity(
                CaseTask,
                case.case_id,
                RESOLVE_FINDINGS_TASK_ROW_KEY,
            ),
        )
        if resolve_task is not None:
            self._storage.upsert_table_entity(
                resolve_task.model_copy(
                    update={
                        "status": "completed",
                        "blocking_gate": None,
                        "updated_at": updated_at,
                        "updated_by_actor_id": actor.actor_id,
                        "updated_by_role": HR_WORKFLOW_ROLE,
                    }
                )
            )

        gate = cast(
            WorkflowGate | None,
            self._storage.get_table_entity(
                WorkflowGate,
                case.case_id,
                APPLICANT_SET_GATE_ROW_KEY,
            ),
        )
        if gate is not None:
            self._storage.upsert_table_entity(
                gate.model_copy(
                    update={
                        "gate_status": "satisfied",
                        "blocking_reasons": [],
                        "last_checked_at": updated_at,
                        "satisfied_by_event_id": event_id,
                        "updated_at": updated_at,
                        "updated_by_actor_id": actor.actor_id,
                        "updated_by_role": HR_WORKFLOW_ROLE,
                    }
                )
            )

        assessment_gate = cast(
            WorkflowGate | None,
            self._storage.get_table_entity(
                WorkflowGate,
                case.case_id,
                ASSESSMENT_GATE_ROW_KEY,
            ),
        )
        if assessment_gate is not None and assessment_gate.gate_status not in {
            "satisfied",
            "waived",
        }:
            self._storage.upsert_table_entity(
                assessment_gate.model_copy(
                    update={
                        "gate_status": "locked",
                        "blocking_reasons": [
                            "Assessment remains locked until a later readiness/assessment slice explicitly unlocks it."
                        ],
                        "last_checked_at": updated_at,
                        "updated_at": updated_at,
                        "updated_by_actor_id": actor.actor_id,
                        "updated_by_role": HR_WORKFLOW_ROLE,
                    }
                )
            )

        self._storage.upsert_table_entity(
            case.model_copy(
                update={
                    "case_status": "applicants_pending",
                    "current_stage": "stage_6_assessment_readiness_pending",
                    "current_gate": "assessment_unlocked",
                    "applicant_set_version": applicant_set_version,
                    "updated_at": updated_at,
                    "updated_by_actor_id": actor.actor_id,
                    "updated_by_role": HR_WORKFLOW_ROLE,
                }
            )
        )

    def _findings_for_candidate(
        self,
        applicant: Applicant,
        documents: list[SourceDocument],
    ) -> list[ImportFinding]:
        if any(document.document_type == REQUIRED_DOCUMENT_TYPE for document in documents):
            return []
        return [
            ImportFinding(
                finding_id=f"missing_resume#{applicant.candidate_id}",
                candidate_id=applicant.candidate_id,
                candidate_ref=applicant.candidate_ref,
                severity="blocking",
                finding_type="missing_required_resume",
                message=(
                    f"Candidate {applicant.candidate_ref} is missing the required resume."
                ),
            )
        ]

    def _compute_findings(
        self,
        case_id: str,
        applicants: list[Applicant],
    ) -> list[ImportFinding]:
        findings: list[ImportFinding] = []
        for applicant in applicants:
            documents = self._list_candidate_documents(case_id, applicant.candidate_id)
            findings.extend(self._findings_for_candidate(applicant, documents))
        return findings

    def _can_confirm(
        self,
        applicants: list[Applicant],
        packages: list[CandidatePackage],
        findings: list[ImportFinding],
    ) -> bool:
        if not applicants:
            return False
        if any(finding.severity == "blocking" for finding in findings):
            return False
        packages_by_candidate = {package.candidate_id: package for package in packages}
        return all(
            packages_by_candidate.get(applicant.candidate_id) is not None
            and packages_by_candidate[applicant.candidate_id].package_status == "complete"
            for applicant in applicants
        )

    def _first_duplicate_ref(
        self,
        active_applicants: list[Applicant],
        new_refs: list[str],
    ) -> str | None:
        seen = {
            self._normalize_candidate_ref(applicant.candidate_ref): applicant.candidate_ref
            for applicant in active_applicants
        }
        for candidate_ref in new_refs:
            normalized = self._normalize_candidate_ref(candidate_ref)
            if normalized in seen:
                return candidate_ref
            seen[normalized] = candidate_ref
        return None

    def _first_unsupported_document_type(
        self,
        request: ApplicantImportRequest,
    ) -> str | None:
        for candidate in request.candidates:
            for document in candidate.documents:
                if document.document_type.strip().casefold() not in ALLOWED_DOCUMENT_TYPES:
                    return document.document_type
        return None

    def _normalize_candidate_ref(self, candidate_ref: str) -> str:
        return candidate_ref.strip().casefold()

    def _event(
        self,
        *,
        case: RecruitmentCase,
        actor: ActorContext,
        event_id: str,
        created_at: str,
        event_type: str,
        summary: str,
        safe_details: dict[str, object],
        candidate_id: str | None = None,
        artifact_id: str | None = None,
        artifact_version: str | None = None,
    ) -> CaseEvent:
        return CaseEvent(
            PartitionKey=case.case_id,
            RowKey=f"{created_at}#{event_id}",
            created_at=created_at,
            created_by_actor_id=actor.actor_id,
            created_by_role=HR_WORKFLOW_ROLE,
            correlation_id=case.correlation_id,
            case_id=case.case_id,
            event_id=event_id,
            event_type=event_type,
            actor_id=actor.actor_id,
            actor_role=HR_WORKFLOW_ROLE,
            candidate_id=candidate_id,
            artifact_id=artifact_id,
            artifact_version=artifact_version,
            summary=summary,
            safe_details=safe_details,
        )

    def _safe_document_ref(self, document: SourceDocument) -> dict[str, object]:
        return {
            "document_id": document.document_id,
            "candidate_id": document.candidate_id,
            "document_type": document.document_type,
            "source_origin": document.source_origin,
            "source_label": document.source_label,
            "blob_path": document.blob_path,
            "mime_type": document.mime_type,
            "file_name": document.file_name,
            "size_bytes": document.size_bytes if document.size_bytes is not None else 0,
            "sha256": document.sha256,
            "processing_status": document.processing_status,
            "version": document.version,
            "created_at": document.created_at,
            "synthetic": document.synthetic,
        }

    def _applicant_summary(self, applicant: Applicant) -> ApplicantSummary:
        return ApplicantSummary(
            candidate_id=applicant.candidate_id,
            candidate_ref=applicant.candidate_ref,
            display_label=applicant.display_label,
            import_status=applicant.import_status,
            applicant_set_version=applicant.applicant_set_version,
            duplicate_group_id=applicant.duplicate_group_id,
            blocking_findings=applicant.blocking_findings,
            created_at=applicant.created_at,
            synthetic=applicant.synthetic,
        )

    def _document_summary(self, document: SourceDocument) -> CandidateDocumentSummary:
        return CandidateDocumentSummary(
            document_id=document.document_id,
            candidate_id=document.candidate_id or "",
            document_type=document.document_type,
            source_origin=document.source_origin,
            source_label=document.source_label,
            blob_path=document.blob_path,
            mime_type=document.mime_type,
            file_name=document.file_name,
            size_bytes=document.size_bytes if document.size_bytes is not None else 0,
            sha256=document.sha256,
            processing_status=document.processing_status,
            version=document.version,
            created_at=document.created_at,
            synthetic=document.synthetic,
        )

    def _package_summary(self, package: CandidatePackage) -> CandidatePackageSummary:
        return CandidatePackageSummary(
            candidate_id=package.candidate_id,
            package_version=package.package_version,
            rubric_version=package.rubric_version,
            document_ids=package.document_ids,
            required_document_status=package.required_document_status,
            package_status=package.package_status,
            blob_path=package.blob_path,
            sha256=package.sha256,
            created_at=package.created_at,
            synthetic=package.synthetic,
        )
