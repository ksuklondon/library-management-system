/**
 * Strona Profile - profil i edycja danych użytkownika.
 *
 * Zgodność z wymaganiami:
 * - F20: Edycja profilu użytkownika
 * - NF7: Walidacja danych wejściowych
 */

import { AlertCircle, CheckCircle, Edit, Save, User as UserIcon, X } from "lucide-react";
import React, { FormEvent, useEffect, useState } from "react";
import { updateUser } from "../../api/auth";
import Button from "../../components/Button";
import Input from "../../components/Input";
import { useAuth } from "../../hooks/useAuth";
import { formatDate } from "../../utils/formatters";
import { isValidEmail, validatePassword } from "../../utils/validators";

/**
 * Komponent Profile - profil użytkownika (F20).
 */
const Profile: React.FC = () => {
  const { user, refreshUser } = useAuth();
  const [isEditing, setIsEditing] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [successMessage, setSuccessMessage] = useState("");

  // Stan formularza
  const [formData, setFormData] = useState({
    email: user?.email || "",
    fullName: user?.full_name || "",
    currentPassword: "",
    newPassword: "",
    confirmPassword: "",
  });

  const [errors, setErrors] = useState<{
    email?: string;
    fullName?: string;
    currentPassword?: string;
    newPassword?: string;
    confirmPassword?: string;
    general?: string;
  }>({});

  /**
   * Aktualizuj formularz gdy user się zmieni.
   */
  useEffect(() => {
    if (user) {
      setFormData({
        email: user.email,
        fullName: user.full_name || "",
        currentPassword: "",
        newPassword: "",
        confirmPassword: "",
      });
    }
  }, [user]);

  /**
   * Aktualizuj pole formularza.
   */
  const handleChange = (field: string, value: string) => {
    setFormData({ ...formData, [field]: value });
    // Wyczyść błąd dla tego pola
    setErrors({ ...errors, [field]: undefined });
  };

  /**
   * Walidacja formularza (NF7).
   */
  const validateForm = (): boolean => {
    const newErrors: any = {};

    // Email
    if (!formData.email.trim()) {
      newErrors.email = "Email jest wymagany";
    } else if (!isValidEmail(formData.email)) {
      newErrors.email = "Nieprawidłowy format email";
    }

    // Jeśli użytkownik chce zmienić hasło
    if (formData.newPassword || formData.confirmPassword) {
      // Sprawdź aktualne hasło
      if (!formData.currentPassword) {
        newErrors.currentPassword = "Podaj aktualne hasło";
      }

      // Waliduj nowe hasło
      const passwordValidation = validatePassword(formData.newPassword);
      if (!passwordValidation.isValid) {
        newErrors.newPassword = passwordValidation.errors[0];
      }

      // Sprawdź potwierdzenie
      if (formData.newPassword !== formData.confirmPassword) {
        newErrors.confirmPassword = "Hasła nie są identyczne";
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  /**
   * Obsługa wysłania formularza (F20).
   */
  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setErrors({});
    setSuccessMessage("");

    // Walidacja
    if (!validateForm()) {
      return;
    }

    if (!user) return;

    setIsLoading(true);

    try {
      // Przygotuj dane do aktualizacji
      const updateData: any = {
        email: formData.email,
        full_name: formData.fullName || undefined,
      };

      // Jeśli zmiana hasła
      if (formData.newPassword) {
        updateData.password = formData.newPassword;
      }

      // Wywołaj API aktualizacji (F20)
      await updateUser(user.id, updateData);

      // Odśwież dane użytkownika
      await refreshUser();

      // Sukces
      setSuccessMessage("Profil zaktualizowany pomyślnie!");
      setIsEditing(false);

      // Wyczyść pola haseł
      setFormData({
        ...formData,
        currentPassword: "",
        newPassword: "",
        confirmPassword: "",
      });

      // Ukryj komunikat po 3 sekundach
      setTimeout(() => setSuccessMessage(""), 3000);
    } catch (error: any) {
      console.error("Update profile error:", error);
      setErrors({
        general: error.message || "Nie udało się zaktualizować profilu",
      });
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Anuluj edycję.
   */
  const handleCancel = () => {
    setIsEditing(false);
    setErrors({});
    setSuccessMessage("");
    // Przywróć oryginalne dane
    if (user) {
      setFormData({
        email: user.email,
        fullName: user.full_name || "",
        currentPassword: "",
        newPassword: "",
        confirmPassword: "",
      });
    }
  };

  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p className="text-gray-600 dark:text-gray-400">Ładowanie profilu...</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-3xl mx-auto">
        {/* Nagłówek */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 mb-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="p-4 bg-blue-100 dark:bg-blue-900 rounded-full">
                <UserIcon size={32} className="text-blue-600 dark:text-blue-400" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                  {user.full_name || user.email}
                </h1>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  {user.role === "ADMIN" && "👑 Administrator"}
                  {user.role === "LIBRARIAN" && "📚 Bibliotekarz"}
                  {user.role === "READER" && "📖 Czytelnik"}
                </p>
              </div>
            </div>

            {!isEditing && (
              <Button
                variant="outline"
                onClick={() => setIsEditing(true)}
                className="flex items-center gap-2"
              >
                <Edit size={18} />
                Edytuj profil
              </Button>
            )}
          </div>
        </div>

        {/* Komunikat sukcesu */}
        {successMessage && (
          <div className="mb-6 rounded-md bg-green-50 dark:bg-green-900/20 p-4 border border-green-200 dark:border-green-800">
            <div className="flex">
              <CheckCircle className="h-5 w-5 text-green-400" />
              <div className="ml-3">
                <p className="text-sm text-green-800 dark:text-green-200">{successMessage}</p>
              </div>
            </div>
          </div>
        )}

        {/* Formularz profilu */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
          <form onSubmit={handleSubmit}>
            <div className="space-y-6">
              {/* Informacje podstawowe */}
              <div>
                <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                  Informacje podstawowe
                </h2>

                <div className="space-y-4">
                  {/* Email */}
                  <Input
                    label="Adres email"
                    type="email"
                    value={formData.email}
                    onChange={(e) => handleChange("email", e.target.value)}
                    error={errors.email}
                    disabled={!isEditing || isLoading}
                    fullWidth
                    required
                  />

                  {/* Imię i nazwisko */}
                  <Input
                    label="Imię i nazwisko"
                    type="text"
                    value={formData.fullName}
                    onChange={(e) => handleChange("fullName", e.target.value)}
                    error={errors.fullName}
                    disabled={!isEditing || isLoading}
                    fullWidth
                  />

                  {/* Rola (tylko do odczytu) */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                      Rola w systemie
                    </label>
                    <input
                      type="text"
                      value={user.role}
                      disabled
                      className="block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-gray-100 dark:bg-gray-700 text-gray-500 dark:text-gray-400"
                    />
                  </div>

                  {/* Data rejestracji (tylko do odczytu) */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                      Data rejestracji
                    </label>
                    <input
                      type="text"
                      value={formatDate(user.created_at)}
                      disabled
                      className="block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-gray-100 dark:bg-gray-700 text-gray-500 dark:text-gray-400"
                    />
                  </div>
                </div>
              </div>

              {/* Zmiana hasła (tylko w trybie edycji) */}
              {isEditing && (
                <div>
                  <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                    Zmiana hasła
                  </h2>
                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
                    Pozostaw puste jeśli nie chcesz zmieniać hasła
                  </p>

                  <div className="space-y-4">
                    {/* Aktualne hasło */}
                    <Input
                      label="Aktualne hasło"
                      type="password"
                      value={formData.currentPassword}
                      onChange={(e) => handleChange("currentPassword", e.target.value)}
                      error={errors.currentPassword}
                      disabled={isLoading}
                      fullWidth
                    />

                    {/* Nowe hasło */}
                    <Input
                      label="Nowe hasło"
                      type="password"
                      value={formData.newPassword}
                      onChange={(e) => handleChange("newPassword", e.target.value)}
                      error={errors.newPassword}
                      disabled={isLoading}
                      fullWidth
                      helperText="Min. 8 znaków, wielka litera, mała litera, cyfra"
                    />

                    {/* Potwierdź nowe hasło */}
                    <Input
                      label="Potwierdź nowe hasło"
                      type="password"
                      value={formData.confirmPassword}
                      onChange={(e) => handleChange("confirmPassword", e.target.value)}
                      error={errors.confirmPassword}
                      disabled={isLoading}
                      fullWidth
                    />
                  </div>
                </div>
              )}

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

              {/* Przyciski akcji */}
              {isEditing && (
                <div className="flex gap-3 pt-4">
                  <Button
                    type="submit"
                    variant="primary"
                    isLoading={isLoading}
                    disabled={isLoading}
                    className="flex items-center gap-2"
                  >
                    <Save size={18} />
                    Zapisz zmiany
                  </Button>
                  <Button
                    type="button"
                    variant="outline"
                    onClick={handleCancel}
                    disabled={isLoading}
                    className="flex items-center gap-2"
                  >
                    <X size={18} />
                    Anuluj
                  </Button>
                </div>
              )}
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default Profile;
