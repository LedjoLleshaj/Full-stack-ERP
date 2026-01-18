/**
 * Environment configuration - Production
 * API endpoints grouped by domain with legacy flat keys for backward compatibility
 */
export const environment = {
  production: true,
  apiUrl: 'https://api.selita-fish.com/selita', // TODO: Update with actual production URL

  // ========= GROUPED ENDPOINTS (for future use) =========
  auth: {
    login: '/login',
    refreshToken: '/api/token/refresh/',
  },
  products: {
    getAll: '/products',
    getById: '/productbyid',
    add: '/add-product',
    getCategories: '/product-categories',
    getNames: '/product-names',
    updatePrice: '/update-price/',
    filterByCategories: '/filterbycategories',
    checkDisponibility: '/checkdisponibility/',
  },
  sales: {
    getAll: '/salesinfo',
    create: '/create-sale',
    pay: '/pay-sale/',
    getDetails: '/sale-details/',
    getLastSoldPrice: '/last-sold-price',
    report: '/report/sales/',
  },
  clients: {
    getAll: '/clients',
    getById: '/client/',
    add: '/add-client',
  },
  reports: {
    dashboardStats: '/dashboard-stats',
    dailyProfit: '/daily-profit',
  },
  inventory: {
    update: '/update-inventory',
  },

  // ========= LEGACY FLAT KEYS (for backward compatibility) =========
  login: '/login',
  refreshToken: '/api/token/refresh/',
  addProduct: '/add-product',
  getProducts: '/products',
  getProductCategories: '/product-categories',
  getProductNames: '/product-names',
  updatePrice: '/update-price/',
  filterByCategories: '/filterbycategories',
  getSales: '/salesinfo',
  productbyid: '/productbyid',
  getClients: '/clients',
  paySale: '/pay-sale/',
  createSale: '/create-sale',
  updateInventory: '/update-inventory',
  checkdisponibility: '/checkdisponibility/',
  getClientById: '/client/',
  addClient: '/add-client',
  getLastSoldPrice: '/last-sold-price',
  salesReport: '/report/sales/',
  dashboardStats: '/dashboard-stats',
  getSaleDetails: '/sale-details/',
  dailyProfit: '/daily-profit',
};
