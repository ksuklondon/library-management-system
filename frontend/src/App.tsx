/**
 * App - główny komponent aplikacji z routingiem.
 */

import { Route, BrowserRouter as Router, Routes } from "react-router-dom";
import Footer from "./components/Footer";
import Navbar from "./components/Navbar";
import ProtectedRoute from "./components/ProtectedRoute";
import { AuthProvider } from "./context/AuthContext";
import { ThemeProvider } from "./context/ThemeContext";
import { UserRole } from "./types/user";

// Pages - Auth
import Login from "./pages/auth/Login";
import Profile from "./pages/auth/Profile";
import Register from "./pages/auth/Register";

// Pages - Public
import Home from "./pages/Home";

// Pages - Catalog
import BookDetails from "./pages/catalog/BookDetails";
import Catalog from "./pages/catalog/Catalog";

// Pages - User
import MyFines from "./pages/user/MyFines";
import MyLoans from "./pages/user/MyLoans";
import MyReservations from "./pages/user/MyReservations";

// Pages - Librarian
import IssueBook from "./pages/librarian/IssueBook";
import LibrarianPanel from "./pages/librarian/LibrarianPanel";
import ManageBooks from "./pages/librarian/ManageBooks";
import ManageCopies from "./pages/librarian/ManageCopies";
import ManageUsers from "./pages/librarian/ManageUsers";
import ReturnBook from "./pages/librarian/ReturnBook";

// Pages - Admin
import AdminPanel from "./pages/admin/AdminPanel";
import AuditLogs from "./pages/admin/AuditLogs";
import UserRoles from "./pages/admin/UserRoles";

function App() {
  return (
    <Router>
      <ThemeProvider>
        <AuthProvider>
          <div className="min-h-screen flex flex-col bg-gray-50 dark:bg-gray-900">
            <Navbar />

            <main className="flex-1">
              <Routes>
                {/* Public Routes */}
                <Route path="/" element={<Home />} />
                <Route path="/login" element={<Login />} />
                <Route path="/register" element={<Register />} />

                {/* Catalog Routes - Public */}
                <Route path="/catalog" element={<Catalog />} />
                <Route path="/book/:id" element={<BookDetails />} />

                {/* Protected Routes - Authenticated Users */}
                <Route
                  path="/profile"
                  element={
                    <ProtectedRoute>
                      <Profile />
                    </ProtectedRoute>
                  }
                />

                {/* Protected Routes - User */}
                <Route
                  path="/my-reservations"
                  element={
                    <ProtectedRoute>
                      <MyReservations />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/my-loans"
                  element={
                    <ProtectedRoute>
                      <MyLoans />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/my-fines"
                  element={
                    <ProtectedRoute>
                      <MyFines />
                    </ProtectedRoute>
                  }
                />

                {/* Protected Routes - Librarian */}
                <Route
                  path="/librarian"
                  element={
                    <ProtectedRoute roles={[UserRole.LIBRARIAN, UserRole.ADMIN]}>
                      <LibrarianPanel />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/librarian/issue"
                  element={
                    <ProtectedRoute roles={[UserRole.LIBRARIAN, UserRole.ADMIN]}>
                      <IssueBook />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/librarian/return"
                  element={
                    <ProtectedRoute roles={[UserRole.LIBRARIAN, UserRole.ADMIN]}>
                      <ReturnBook />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/librarian/books"
                  element={
                    <ProtectedRoute roles={[UserRole.LIBRARIAN, UserRole.ADMIN]}>
                      <ManageBooks />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/librarian/copies"
                  element={
                    <ProtectedRoute roles={[UserRole.LIBRARIAN, UserRole.ADMIN]}>
                      <ManageCopies />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/librarian/users"
                  element={
                    <ProtectedRoute roles={[UserRole.LIBRARIAN, UserRole.ADMIN]}>
                      <ManageUsers />
                    </ProtectedRoute>
                  }
                />

                {/* Protected Routes - Admin */}
                <Route
                  path="/admin"
                  element={
                    <ProtectedRoute roles={[UserRole.ADMIN]}>
                      <AdminPanel />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/admin/user-roles"
                  element={
                    <ProtectedRoute roles={[UserRole.ADMIN]}>
                      <UserRoles />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/admin/audit-logs"
                  element={
                    <ProtectedRoute roles={[UserRole.ADMIN]}>
                      <AuditLogs />
                    </ProtectedRoute>
                  }
                />

                {/* 404 */}
                <Route
                  path="*"
                  element={
                    <div className="min-h-screen flex items-center justify-center">
                      <div className="text-center">
                        <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-4">
                          404
                        </h1>
                        <p className="text-gray-600 dark:text-gray-400 mb-4">
                          Strona nie została znaleziona
                        </p>
                        <button
                          onClick={() => (window.location.href = "/")}
                          className="text-blue-600 dark:text-blue-400 hover:underline"
                        >
                          Wróć do strony głównej
                        </button>
                      </div>
                    </div>
                  }
                />
              </Routes>
            </main>

            <Footer />
          </div>
        </AuthProvider>
      </ThemeProvider>
    </Router>
  );
}

export default App;
