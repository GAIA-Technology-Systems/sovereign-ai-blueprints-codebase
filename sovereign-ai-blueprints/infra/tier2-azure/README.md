# Tier 2 infrastructure — private endpoint in your own tenant

`main.bicep` deploys the shape the scenario 2 diagram claims:

- an Azure AI / OpenAI account with `publicNetworkAccess: Disabled`
- a private endpoint in your VNet, with a private DNS zone so the
  `privatelink` hostname resolves inside the tenant only
- diagnostic settings writing to a storage account **you** own
- no API keys: `disableLocalAuth` is on, and the app authenticates with a managed
  identity holding the `Cognitive Services OpenAI User` role

```bash
az deployment group create -g rg-sovereign -f infra/tier2-azure/main.bicep \
  -p vnetName=vnet-sovereign subnetName=snet-ai
```

The client in `src/sovereign/providers/tier2_private_endpoint.py` refuses to start
against a public hostname, so the code and the infrastructure fail together rather
than drifting apart.
