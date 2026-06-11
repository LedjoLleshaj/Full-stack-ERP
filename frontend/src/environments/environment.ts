/**
 * Environment configuration - Development
 * API endpoints grouped by domain with legacy flat keys for backward compatibility
 */
export const environment = {
  production: false,
  apiUrl: 'http://localhost:8080/erp',

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
    invoice: '/transaction/',
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
  invoice: '/transaction/',
};
