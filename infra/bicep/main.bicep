// =============================================================================
// PLACEHOLDER ONLY — NOT DEPLOYED, NOT VALIDATED, NOT APPROVED.
// Live Azure/Foundry wiring is human-gated (deferred ADR + BQ-005 region
// approval). No real tenant/subscription IDs, endpoints, or secrets anywhere.
// Identity-based access only: managed identity + RBAC; no keys/SAS/connstrings.
// =============================================================================

targetScope = 'resourceGroup' // resource group itself created out-of-band; suggested name: rg-hrha-lab-cac

@description('Placeholder: lab resource name prefix')
param namePrefix string = 'hrhalab'

@description('Placeholder: region — pending BQ-005 Canadian-residency approval; never adopt silently')
param location string = 'TODO-approved-canadian-region' // e.g. canadacentral, ONLY after human approval

// --- Storage (full records + artifact tree in blob; metadata rows in tables) ---
resource storage 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: '${namePrefix}stor' // TODO: final name; 3-24 lowercase alphanumerics
  location: location
  sku: { name: 'Standard_LRS' }
  kind: 'StorageV2'
  properties: {
    allowSharedKeyAccess: false // identity-based access only
    minimumTlsVersion: 'TLS1_2'
  }
}

resource blobService 'Microsoft.Storage/storageAccounts/blobServices@2023-01-01' = {
  parent: storage
  name: 'default'
}

resource evaluationsContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-01-01' = {
  parent: blobService
  name: 'hrha-evaluations' // mirrors local layout: evaluations/{evaluation_id}/...
}

// --- Facade host (candidate: Azure Functions) ---
resource functionApp 'Microsoft.Web/sites@2023-01-01' = {
  name: '${namePrefix}-func' // TODO: final Function App name
  location: location
  kind: 'functionapp,linux'
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${managedIdentity.id}': {}
    }
  }
  properties: {
    httpsOnly: true
    // App settings are placeholders; see infra/env.sample. No secrets here.
  }
}

// --- Observability (safe metadata only; never-log rules apply) ---
resource appInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: '${namePrefix}-appi'
  location: location
  kind: 'web'
  properties: { Application_Type: 'web' }
}

// --- Key Vault (future secrets that managed identity cannot eliminate; none known today) ---
resource keyVault 'Microsoft.KeyVault/vaults@2023-07-01' = {
  name: '${namePrefix}-kv'
  location: location
  properties: {
    sku: { family: 'A', name: 'standard' }
    tenantId: subscription().tenantId // resolved at deploy time; never hardcoded
    enableRbacAuthorization: true
  }
}

// --- Identity + RBAC placeholders ---
resource managedIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: '${namePrefix}-mi'
  location: location
}

// TODO (placeholder, not active): role assignments for the managed identity —
//   Storage Blob Data Contributor + Storage Table Data Contributor on `storage`,
//   Key Vault Secrets User on `keyVault`, plus the Foundry data-plane role the
//   deferred ADR selects. Entra group object IDs for `hr`/`admin_lab` access
//   are supplied at wiring time through an approved channel (never committed).

// --- Azure AI Foundry placeholders (runtime shape = deferred ADR question) ---
// TODO (placeholder, not active): Foundry resource + project. Whether council
// roles run as project Responses API calls, prompt agents, or hosted agents is
// the deferred ADR's decision; nothing is chosen here.
