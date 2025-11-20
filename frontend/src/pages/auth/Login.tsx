/**
 * Strona Login - logowanie użytkownika.
 *
 * Zgodność z wymaganiami:
 * - F2: Logowanie użytkownika
 * - NF7: Walidacja danych wejściowych
 * - NF4: JWT tokens
 */

import React, { useState, FormEvent } from 'react';
import { useNavigate, useLocation, Link } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import { LogIn, Mail, Lock, AlertCircle } from 'lucide-react';
import Input from '../../components/Input';
import Button from '../../components/Button';
import { isValidEmail } from '../../utils/validators';

/**
 * Komponent Login - formularz logowania (F2).
 */
const Login: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { login, isLoading } = useAuth();

  // Stan formularza
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [errors, setErrors] = useState<{ email?: string; password?: string; general?: string }>({});

  // Skąd użytkownik przyszedł (do przekierowania po logowaniu)
  const from = (location.state as any)?.from?.pathname || '/';

  /**
   * Walidacja formularza (NF7).
   */
  const validateForm = (): boolean => {
    const newErrors: { email?: string; password?: string } = {};

    // Walidacja email
    if (!email.trim()) {
      newErrors.email = 'Email jest wymagany';
    } else if (!isValidEmail(email)) {
      newErrors.email = 'Nieprawidłowy format email';
    }

    // Walidacja hasła
    if (!password) {
      newErrors.password = 'Hasło jest wymagane';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  /**
   * Obsługa wysłania formularza (F2).
   */
  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setErrors({});

    // Walidacja
    if (!validateForm()) {
      return;
    }

    try {
      // Wywołaj login z AuthContext (F2, NF4)
      await login({ email, password });

      // Przekieruj do poprzedniej strony lub strony głównej
      navigate(from, { replace: true });
    } catch (error: any) {
      console.error('Login error:', error);
      setErrors({
        general: error.message || 'Nieprawidłowy email lub hasło',
      });
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        {/* Logo i nagłówek */}
        <div className="text-center">
          <div className="flex justify-center mb-4">
            <LogIn size={48} className="text-blue-600 dark:text-blue-400" />
          </div>
          <h2 className="text-3xl font-bold text-gray-900 dark:text-white">
            Zaloguj się
          </h2>
          <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
            Lub{' '}
            <Link
              to="/register"
              className="font-medium text-blue-600 dark:text-blue-400 hover:text-blue-500"
            >
              utwórz nowe konto
            </Link>
          </p>
        </div>

        {/* Formularz logowania */}
        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          <div className="space-y-4">
            {/* Pole Email (F2) */}
            <Input
              label="Adres email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              error={errors.email}
              placeholder="jan@example.com"
              required
              fullWidth
              disabled={isLoading}
            />

            {/* Pole Hasło (F2) */}
            <Input
              label="Hasło"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              error={errors.password}
              placeholder="••••••••"
              required
              fullWidth
              disabled={isLoading}
            />
          </div>

          {/* Błąd ogólny */}
          {errors.general && (
            <div className="rounded-md bg-red-50 dark:bg-red-900/20 p-4 border border-red-200 dark:border-red-800">
              <div className="flex">
                <AlertCircle className="h-5 w-5 text-red-400" />
                <div className="ml-3">
                  <p className="text-sm text-red-800 dark:text-red-200">
                    {errors.general}
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Przycisk zaloguj */}
          <Button
            type="submit"
            variant="primary"
            fullWidth
            isLoading={isLoading}
            disabled={isLoading}
          >
            Zaloguj się
          </Button>

          {/* Link do resetowania hasła (opcjonalnie) */}
          <div className="text-center">

              href="#"
              className="text-sm font-medium text-blue-600 dark:text-blue-400 hover:text-blue-500"
            >
              Zapomniałeś hasła?
            </a>
          </div>
        </form>

        {/* Informacja o demo (dla celów testowych) */}
        <div className="mt-6 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
          <p className="text-sm text-blue-800 dark:text-blue-200 font-medium mb-2">
            Konta demo:
          </p>
          <ul className="text-xs text-blue-700 dark:text-blue-300 space-y-1">
            <li>👤 Czytelnik: reader@example.com / Password123</li>
            <li>📚 Bibliotekarz: librarian@example.com / Password123</li>
            <li>🔧 Admin: admin@example.com / Password123</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default Login;
