/**
 * Tenant-specific API endpoints
 * Useful for getting tenant config from frontend
 */

import { getTenantConfig, tenantExists, getAllTenantIds } from './tenantConfig.js';

export function setupTenantEndpoints(app) {
  /**
   * Get tenant configuration
   * Frontend uses this to get branding, colors, etc.
   */
  app.get('/tenant/:tenantId/config', (req, res) => {
    const { tenantId } = req.params;
    
    if (!tenantExists(tenantId)) {
      return res.status(404).json({ error: `Unknown tenant: ${tenantId}` });
    }
    
    const config = getTenantConfig(tenantId);
    
    // Return public config (hide system prompt)
    res.json({
      tenantId,
      name: config.name,
      displayName: config.displayName,
      colors: config.colors,
    });
  });

  /**
   * List all tenants (useful for debugging/admin)
   */
  app.get('/tenants', (req, res) => {
    const tenantIds = getAllTenantIds();
    const tenants = tenantIds.map(id => {
      const config = getTenantConfig(id);
      return {
        tenantId: id,
        name: config.name,
        displayName: config.displayName,
      };
    });
    
    res.json({ tenants });
  });
}

