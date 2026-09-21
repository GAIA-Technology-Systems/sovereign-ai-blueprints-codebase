// Tier 2 — model deployment reachable only over private networking.
// Illustrative: review naming, SKUs and policy against your own landing zone.

param location string = resourceGroup().location
param accountName string = 'aoai-sovereign-${uniqueString(resourceGroup().id)}'
param vnetName string
param subnetName string
param logStorageName string = 'stsovereign${uniqueString(resourceGroup().id)}'

resource account 'Microsoft.CognitiveServices/accounts@2024-10-01' = {
  name: accountName
  location: location
  kind: 'OpenAI'
  sku: { name: 'S0' }
  identity: { type: 'SystemAssigned' }
  properties: {
    customSubDomainName: accountName
    publicNetworkAccess: 'Disabled'      // the whole point of tier 2
    disableLocalAuth: true               // Entra ID only, no keys on disk
    networkAcls: { defaultAction: 'Deny' }
  }
}

resource vnet 'Microsoft.Network/virtualNetworks@2023-11-01' existing = {
  name: vnetName
}

resource privateEndpoint 'Microsoft.Network/privateEndpoints@2023-11-01' = {
  name: '${accountName}-pe'
  location: location
  properties: {
    subnet: { id: '${vnet.id}/subnets/${subnetName}' }
    privateLinkServiceConnections: [
      {
        name: '${accountName}-plsc'
        properties: {
          privateLinkServiceId: account.id
          groupIds: [ 'account' ]
        }
      }
    ]
  }
}

resource dnsZone 'Microsoft.Network/privateDnsZones@2020-06-01' = {
  name: 'privatelink.openai.azure.com'
  location: 'global'
}

resource dnsLink 'Microsoft.Network/privateDnsZones/virtualNetworkLinks@2020-06-01' = {
  parent: dnsZone
  name: '${vnetName}-link'
  location: 'global'
  properties: {
    registrationEnabled: false
    virtualNetwork: { id: vnet.id }
  }
}

resource dnsGroup 'Microsoft.Network/privateEndpoints/privateDnsZoneGroups@2023-11-01' = {
  parent: privateEndpoint
  name: 'default'
  properties: {
    privateDnsZoneConfigs: [
      { name: 'openai', properties: { privateDnsZoneId: dnsZone.id } }
    ]
  }
}

// Audit and diagnostics land in storage you control.
resource logStorage 'Microsoft.Storage/storageAccounts@2023-05-01' = {
  name: logStorageName
  location: location
  sku: { name: 'Standard_LRS' }
  kind: 'StorageV2'
  properties: {
    allowBlobPublicAccess: false
    minimumTlsVersion: 'TLS1_2'
  }
}

resource diagnostics 'Microsoft.Insights/diagnosticSettings@2021-05-01-preview' = {
  name: '${accountName}-diag'
  scope: account
  properties: {
    storageAccountId: logStorage.id
    logs: [ { categoryGroup: 'audit', enabled: true } ]
  }
}

output endpoint string = 'https://${accountName}.privatelink.openai.azure.com'
