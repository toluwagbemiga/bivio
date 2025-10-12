# Bivio POS PWA

A Progressive Web Application for Point of Sale (POS) financial management, built with Vue.js 3 and designed for Nigerian micro-businesses.

## Features

### 🏪 **POS Management**
- Real-time inventory tracking
- Smart transaction categorization
- Multi-payment method support (Cash, Card, Transfer, Mobile Money)
- Barcode scanning support
- Receipt generation

### 💰 **Financial Management**
- Loan applications and management
- Savings accounts and goals
- Auto-save from transactions
- Cash flow analysis
- Business performance metrics

### 🤖 **AI-Powered Features**
- Smart transaction categorization
- Predictive cash flow analysis
- Business insights and recommendations
- Fraud detection
- Risk assessment

### 📱 **PWA Capabilities**
- Offline-first architecture
- Installable on mobile devices
- Push notifications
- Background sync
- Responsive design

### 🇳🇬 **Nigerian Market Focus**
- Local product names support (Hausa, Igbo, Yoruba, Pidgin)
- BVN/NIN integration
- POS device integration
- Bank transfer remark parsing
- Local currency (NGN) support

## Tech Stack

- **Frontend**: Vue.js 3, Vue Router, Pinia
- **Styling**: Tailwind CSS
- **Charts**: Chart.js with Vue-ChartJS
- **PWA**: Workbox, Service Workers
- **Storage**: IndexedDB with LocalForage
- **HTTP Client**: Axios
- **Build Tool**: Vite
- **Backend**: Django REST Framework (separate repository)

## Getting Started

### Prerequisites

- Node.js 16+ 
- npm or yarn
- Backend API running on port 8000

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd bivio/pwa
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Start the development server**
   ```bash
   npm run dev
   ```

4. **Build for production**
   ```bash
   npm run build
   ```

5. **Preview production build**
   ```bash
   npm run preview
   ```

### Environment Setup

Create a `.env` file in the root directory:

```env
VITE_API_BASE_URL=http://localhost:8000/api
VITE_APP_NAME=Bivio POS
VITE_APP_VERSION=1.0.0
```

## Project Structure

```
pwa/
├── src/
│   ├── components/          # Reusable Vue components
│   ├── layouts/            # Layout components
│   ├── pages/              # Page components
│   ├── stores/             # Pinia stores
│   ├── services/           # API services
│   │   └── api/           # API client modules
│   ├── utils/              # Utility functions
│   ├── App.vue            # Main app component
│   ├── main.js            # App entry point
│   └── style.css          # Global styles
├── public/                 # Static assets
├── index.html             # HTML template
├── vite.config.js         # Vite configuration
├── tailwind.config.js     # Tailwind CSS config
└── package.json           # Dependencies
```

## API Integration

The PWA integrates with the Django REST Framework backend through a comprehensive API service layer:

### Available Services

- **Authentication** (`authApi`): User login, registration, profile management
- **Inventory** (`inventoryApi`): Products, categories, stock movements
- **Transactions** (`transactionApi`): Sales, purchases, payments
- **Loans** (`loanApi`): Loan applications, repayments, products
- **Savings** (`savingsApi`): Savings accounts, goals, transactions
- **Analytics** (`analyticsApi`): Business metrics, insights, alerts
- **AI** (`aiApi`): Category predictions, training data
- **Notifications** (`notificationApi`): User notifications, preferences

### Usage Example

```javascript
import { inventoryApi } from '@/services/api/inventory'

// Fetch products
const products = await inventoryApi.getProducts()

// Create new product
const newProduct = await inventoryApi.createProduct({
  name: 'Product Name',
  sku: 'SKU001',
  cost_price: 100.00,
  selling_price: 150.00
})
```

## State Management

The application uses Pinia for state management with dedicated stores:

- **AuthStore**: User authentication and profile
- **InventoryStore**: Product and inventory management
- **TransactionStore**: Transaction data and operations
- **NotificationStore**: Notifications and preferences
- **OfflineStore**: Offline status and sync management

## PWA Features

### Service Worker
- Caches API responses for offline access
- Handles background sync
- Manages push notifications
- Implements cache strategies for different resource types

### Offline Support
- Stores critical data in IndexedDB
- Syncs data when connection is restored
- Shows offline indicators
- Graceful degradation of features

### Installation
- Add to home screen on mobile devices
- Desktop installation support
- App-like experience
- Custom splash screen

## Development

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint
- `npm run format` - Format code with Prettier

### Code Style

The project follows Vue.js and JavaScript best practices:

- Composition API for Vue components
- TypeScript-style JSDoc comments
- Consistent naming conventions
- Component-based architecture
- Responsive design principles

## Deployment

### Production Build

1. **Build the application**
   ```bash
   npm run build
   ```

2. **Deploy the `dist` folder** to your web server

3. **Configure HTTPS** (required for PWA features)

4. **Set up proper caching headers** for static assets

### Environment Variables

Configure production environment variables:

```env
VITE_API_BASE_URL=https://api.bivio.com/api
VITE_APP_NAME=Bivio POS
VITE_APP_VERSION=1.0.0
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support and questions:

- Email: support@bivio.com
- Documentation: [docs.bivio.com](https://docs.bivio.com)
- Issues: [GitHub Issues](https://github.com/bivio/issues)

## Roadmap

### Upcoming Features

- [ ] Advanced reporting and analytics
- [ ] Multi-location support
- [ ] Staff management
- [ ] Advanced AI features
- [ ] Integration with Nigerian banks
- [ ] Mobile app (React Native)
- [ ] Advanced inventory features
- [ ] Customer management
- [ ] Loyalty programs
- [ ] Advanced loan products

### Version History

- **v1.0.0** - Initial release with core POS features
- **v1.1.0** - AI categorization and analytics
- **v1.2.0** - Loan and savings management
- **v1.3.0** - Advanced PWA features
