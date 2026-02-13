/**
 * Tenant Configuration
 * 
 * This file defines branding and settings for each tenant (store).
 * Adding a new store is as simple as adding a new entry here.
 */

export const tenantConfigs = {
  ch: {
    name: 'Cannabis Healing',
    displayName: 'Flight Club',
    tone: 'friendly, street-lux, helpful',
    colors: {
      primary: '#D4AF37',
      primaryLight: '#E5C158',
      secondary: '#1a1a1a',
      background: '#FFFFFF',
    },
    glassOperatorId: '7806c904-80e6-4501-92b8-892ef48c8706',
    systemPrompt: `You are the virtual budtender for Cannabis Healing, a premium dispensary. Your job is to recommend products from the inventory list provided.

Rules:
- ONLY recommend products from the list I give you
- NEVER make medical claims or say products "treat" or "cure" anything
- Describe effects in general terms: relaxing, euphoric, uplifting, sleepy, energizing, etc.
- Always give 2-4 recommendations with short explanations (1-2 sentences each)
- Keep it friendly, clear, and street-lux in tone
- Respond ONLY with valid JSON matching this exact format:

{
  "message": "A brief intro to your recommendations (1-2 sentences)",
  "recommendations": [
    { "id": "product_id", "reason": "why this fits their needs" }
  ]
}`,
  },

  ac: {
    name: 'Advanced Cultivators',
    glassOperatorId: '5cf3e788-7760-437c-a27f-de58a8a71d01',
    systemPrompt: 'You are the virtual budtender for Advanced Cultivators, a premium cannabis cultivator in Lowell, MA. They are the first Latino-owned recreational cultivator in Massachusetts. Help customers find the right products from their menu. Be knowledgeable about flower strains, prerolls, and concentrates. Maintain a premium, welcoming tone.',
    fallbackGreeting: 'Welcome to Advanced Cultivators! I can help you explore our craft cannabis menu. What are you looking for today?'
  },

  // Future tenants can be added here:
  // example: {
  //   name: 'Example Dispensary',
  //   displayName: 'Ask Your Budtender',
  //   tone: 'professional and welcoming',
  //   colors: {
  //     primary: '#4CAF50',
  //     primaryLight: '#66BB6A',
  //     secondary: '#212121',
  //     background: '#FFFFFF',
  //   },
  //   glassOperatorId: 'operator-id',
  //   systemPrompt: '...',
  // },
};

/**
 * Get tenant configuration by ID
 */
export function getTenantConfig(tenantId) {
  const config = tenantConfigs[tenantId];
  if (!config) {
    throw new Error(`Unknown tenant: ${tenantId}`);
  }
  return config;
}

/**
 * Check if tenant exists
 */
export function tenantExists(tenantId) {
  return tenantId in tenantConfigs;
}

/**
 * Get all tenant IDs
 */
export function getAllTenantIds() {
  return Object.keys(tenantConfigs);
}

