import { BrowserRouter } from 'react-router-dom';
// @ts-ignore
import Sidebar from './components/layout/Sidbar';
// @ts-ignore
import ImgLogin from './components/layout/ImgLogin';
// @ts-ignore
import AppRoutes from './routes/AppRoutes';
// @ts-ignore
import { UserProvider } from './context/UserContext';
import './App.css';

function App() {
  return (
    <BrowserRouter>
      <UserProvider>
        <div className="app">
          <Sidebar />
          <ImgLogin />
          <main className="main-content">
            <AppRoutes />
          </main>
        </div>
      </UserProvider>
    </BrowserRouter>
  );
}

export default App;
