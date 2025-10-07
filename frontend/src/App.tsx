import { BrowserRouter } from 'react-router-dom';
// @ts-ignore
import Sidebar from './components/layout/Sidbar';
// @ts-ignore
import AppRoutes from './routes/AppRoutes';
import './App.css';

function App() {
  return (
    <BrowserRouter>
      <div className="app">
        <Sidebar />
        <main className="main-content">
          <AppRoutes />
        </main>
      </div>
    </BrowserRouter>
  );
}

export default App;
