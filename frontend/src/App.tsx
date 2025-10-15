// @ts-ignore
import { BrowserRouter } from 'react-router-dom';
// @ts-ignore
import Sidebar from './components/layout/Sidebar';
// @ts-ignore
import ImgLogin from './components/layout/ImgLogin';
// @ts-ignore
import AppRoutes from './routes/AppRoutes';
// @ts-ignore
import { UserProvider } from './context/UserContext';
// @ts-ignore
import './App.css';

// @ts-ignore
import { initAuthBackgroundTasks } from './api/auth';
initAuthBackgroundTasks(); // appelé une seule fois au chargement du module

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
