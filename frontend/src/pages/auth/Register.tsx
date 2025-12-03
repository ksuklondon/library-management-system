/**
 * Strona Register - rejestracja nowego użytkownika.
 *
 * Zgodność z wymaganiami:
 * - F1: Rejestracja użytkownika
 * - NF7: Walidacja danych wejściowych
 * - NF2: Bezpieczne hasła
 */

import { AlertCircle, CheckCircle, UserPlus } from "lucide-react";
import React, { type FormEvent, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import Button from "../../components/Button";
import Input from "../../components/Input";
import { useAuth } from "../../hooks/useAuth";
import { getPasswordStrength, isValidEmail, validatePassword } from "../../utils/validators";

type RegisterFormData = {
  email: string;
  password: string;
  confirmPassword: string;
  fullName: string;
};

type RegisterErrors = {
  email?: string;
  password?: string;
  confirmPassword?: string;
  fullName?: string;
  general?: string;
};

/**
 * Komponent Register - formularz rejestracji (F1).
 */
const Register: React.FC = () => {
  const navigate = useNavigate();
  const { register, isLoading } = useAuth();

  // Stan formularza
  const [formData, setFormData] = useState<RegisterFormData>({
    email: "",
    password: "",
    confirmPassword: "",
    fullName: "",
  });

  const [errors, setErrors] = useState<RegisterErrors>({});

  const [showPasswordStrength, setShowPasswordStrength] = useState(false);

  /**
   * Aktualizuj pole formularza.
   */
  const handleChange = (field: keyof RegisterFormData, value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }));

    // Pokaż siłę hasła gdy użytkownik zaczyna pisać
    if (field === "password" && value.length > 0) {
      setShowPasswordStrength(true);
    }
  };

  /**
   * Siła hasła (NF2, NF7).
   */
  const passwordStrength = formData.password ? getPasswordStrength(formData.password) : null;

  const strengthConfig = {
    weak: { color: "bg-red-500", text: "Słabe", textColor: "text-red-600" },
    medium: {
      color: "bg-yellow-500",
      text: "Średnie",
      textColor: "text-yellow-600",
    },
    strong: {
      color: "bg-green-500",
      text: "Silne",
      textColor: "text-green-600",
    },
  } as const;

  /**
   * Walidacja formularza (NF7).
   */
  const validateForm = (): boolean => {
    const newErrors: RegisterErrors = {};

    // Email
    if (!formData.email.trim()) {
      newErrors.email = "Email jest wymagany";
    } else if (!isValidEmail(formData.email)) {
      newErrors.email = "Nieprawidłowy format email";
    }

    // Hasło (NF2, NF7)
    const passwordValidation = validatePassword(formData.password);
    if (!passwordValidation.isValid) {
      newErrors.password = passwordValidation.errors[0];
    }

    // Potwierdzenie hasła
    if (!formData.confirmPassword) {
      newErrors.confirmPassword = "Potwierdź hasło";
    } else if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = "Hasła nie są identyczne";
    }

    // Imię i nazwisko (opcjonalne, ale jeśli podane to waliduj)
    if (formData.fullName && formData.fullName.length < 2) {
      newErrors.fullName = "Imię i nazwisko musi mieć minimum 2 znaki";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  /**
   * Obsługa wysłania formularza (F1).
   */
  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setErrors({});

    // Walidacja
    if (!validateForm()) {
      return;
    }

    try {
      // Wywołaj register z AuthContext (F1)
      await register({
        email: formData.email,
        password: formData.password,
        full_name: formData.fullName || undefined,
      });

      // Przekieruj na stronę główną (użytkownik jest automatycznie zalogowany)
      navigate("/");
    } catch (error: unknown) {
      console.error("Registration error:", error);
      const message =
        error instanceof Error ? error.message : "Nie udało się utworzyć konta. Spróbuj ponownie.";
      setErrors({
        general: message,
      });
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        {/* Logo i nagłówek */}
        <div className="text-center">
          <div className="flex justify-center mb-4">
            <UserPlus size={48} className="text-blue-600 dark:text-blue-400" />
          </div>
          <h2 className="text-3xl font-bold text-gray-900 dark:text-white">Utwórz konto</h2>
          <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
            Lub{" "}
            <Link
              to="/login"
              className="font-medium text-blue-600 dark:text-blue-400 hover:text-blue-500"
            >
              zaloguj się na istniejące konto
            </Link>
          </p>
        </div>

        {/* Formularz rejestracji */}
        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          <div className="space-y-4">
            {/* Pole Email (F1) */}
            <Input
              label="Adres email"
              type="email"
              value={formData.email}
              onChange={(e) => handleChange("email", e.target.value)}
              error={errors.email}
              placeholder="jan@example.com"
              required
              fullWidth
              disabled={isLoading}
            />

            {/* Pole Imię i nazwisko (F1 - opcjonalne) */}
            <Input
              label="Imię i nazwisko"
              type="text"
              value={formData.fullName}
              onChange={(e) => handleChange("fullName", e.target.value)}
              error={errors.fullName}
              placeholder="Jan Kowalski"
              fullWidth
              disabled={isLoading}
              helperText="Opcjonalne"
            />

            {/* Pole Hasło (F1, NF2, NF7) */}
            <div>
              <Input
                label="Hasło"
                type="password"
                value={formData.password}
                onChange={(e) => handleChange("password", e.target.value)}
                error={errors.password}
                placeholder="••••••••"
                required
                fullWidth
                disabled={isLoading}
              />

              {/* Wskaźnik siły hasła (NF2) */}
              {showPasswordStrength && formData.password && passwordStrength && (
                <div className="mt-2">
                  <div className="flex items-center gap-2 mb-1">
                    <div className="flex-1 bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                      <div
                        className={`h-2 rounded-full transition-all ${strengthConfig[passwordStrength].color}`}
                        style={{
                          width:
                            passwordStrength === "weak"
                              ? "33%"
                              : passwordStrength === "medium"
                              ? "66%"
                              : "100%",
                        }}
                      />
                    </div>
                    <span
                      className={`text-xs font-medium ${strengthConfig[passwordStrength].textColor}`}
                    >
                      {strengthConfig[passwordStrength].text}
                    </span>
                  </div>
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    Hasło musi zawierać min. 8 znaków, wielką literę, małą literę i cyfrę
                  </p>
                </div>
              )}
            </div>

            {/* Pole Potwierdź hasło (F1, NF7) */}
            <Input
              label="Potwierdź hasło"
              type="password"
              value={formData.confirmPassword}
              onChange={(e) => handleChange("confirmPassword", e.target.value)}
              error={errors.confirmPassword}
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
                  <p className="text-sm text-red-800 dark:text-red-200">{errors.general}</p>
                </div>
              </div>
            </div>
          )}

          {/* Informacja o zgodzie (NF7) */}
          <div className="rounded-md bg-blue-50 dark:bg-blue-900/20 p-4 border border-blue-200 dark:border-blue-800">
            <div className="flex">
              <CheckCircle className="h-5 w-5 text-blue-400" />
              <div className="ml-3">
                <p className="text-xs text-blue-800 dark:text-blue-200">
                  Rejestrując się, akceptujesz nasz{" "}
                  <Link to="/terms" className="underline">
                    regulamin
                  </Link>{" "}
                  i{" "}
                  <Link to="/privacy" className="underline">
                    politykę prywatności
                  </Link>
                  .
                </p>
              </div>
            </div>
          </div>

          {/* Przycisk zarejestruj */}
          <Button
            type="submit"
            variant="primary"
            fullWidth
            isLoading={isLoading}
            disabled={isLoading}
          >
            Utwórz konto
          </Button>
        </form>
      </div>
    </div>
  );
};

export default Register;
