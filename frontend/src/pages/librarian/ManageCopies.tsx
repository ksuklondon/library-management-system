/**
 * Strona ManageCopies - zarządzanie egzemplarzami książek.
 *
 * Zgodność z wymaganiami:
 * - F16: Dodawanie egzemplarzy książek (LIBRARIAN)
 * - NF5: RBAC - dostęp tylko dla LIBRARIAN i ADMIN
 */

import { AlertCircle, Edit, MapPin, Package, Plus, Trash2 } from "lucide-react";
import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import Button from "../../components/Button";
import Input from "../../components/Input";
import Loading from "../../components/Loading";
import { useAuth } from "../../hooks/useAuth";
import { BookCopy } from "../../types/book";

/**
 * Komponent ManageCopies - zarządzanie egzemplarzami (F16).
 */
const ManageCopies: React.FC = () => {
  const navigate = useNavigate();
  const { isLibrarian, isAdmin } = useAuth();

  // Stan danych
  const [copies, setCopies] = useState<BookCopy[]>([]);
  const [selectedBookId, setSelectedBookId] = useState("");

  // Stan UI
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  /**
   * Sprawdź uprawnienia (NF5).
   */
  if (!isLibrarian() && !isAdmin()) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
        <div className="text-center">
          <AlertCircle size={64} className="mx-auto text-red-500 mb-4" />
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">Brak dostępu</h1>
          <p className="text-gray-600 dark:text-gray-400 mb-4">
            Nie masz uprawnień do zarządzania egzemplarzami. Wymagana rola: Bibliotekarz.
          </p>
          <Button onClick={() => navigate("/")}>Wróć do strony głównej</Button>
        </div>
      </div>
    );
  }

  /**
   * Załaduj egzemplarze dla wybranej książki.
   */
  const loadCopies = async () => {
    if (!selectedBookId) return;

    setIsLoading(true);
    setError(null);

    try {
      // W przyszłości: wywołanie API getBookCopies(selectedBookId)
      // Teraz: symulacja danych
      setTimeout(() => {
        setCopies([
          {
            id: "1",
            book_id: selectedBookId,
            inventory_no: "INV-001",
            status: "AVAILABLE",
            location: "Półka A1",
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
          },
          {
            id: "2",
            book_id: selectedBookId,
            inventory_no: "INV-002",
            status: "BORROWED",
            location: "Półka A1",
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
          },
        ]);
        setIsLoading(false);
      }, 500);
    } catch (err: any) {
      console.error("Error loading copies:", err);
      setError(err.message || "Nie udało się załadować egzemplarzy");
      setIsLoading(false);
    }
  };

  /**
   * Obsługa zmiany wybranej książki.
   */
  const handleBookIdChange = (e: React.FormEvent) => {
    e.preventDefault();
    loadCopies();
  };

  /**
   * Dodaj nowy egzemplarz (F16).
   */
  const handleAddCopy = () => {
    if (!selectedBookId) {
      alert("Najpierw wybierz książkę");
      return;
    }
    // W przyszłości: modal lub formularz dodawania egzemplarza
    alert(
      "Funkcja dodawania egzemplarza będzie wkrótce dostępna! (wymaga integracji z Catalog Service)"
    );
  };

  /**
   * Edytuj egzemplarz.
   */
  const handleEditCopy = (copyId: string) => {
    alert(`Edycja egzemplarza ${copyId} będzie wkrótce dostępna!`);
  };

  /**
   * Usuń egzemplarz.
   */
  const handleDeleteCopy = async (copyId: string) => {
    const confirmed = window.confirm("Czy na pewno chcesz usunąć ten egzemplarz?");

    if (!confirmed) return;

    alert(`Usuwanie egzemplarza ${copyId} będzie wkrótce dostępne!`);
  };

  /**
   * Kolory dla statusów egzemplarzy.
   */
  const getStatusColor = (status: string) => {
    switch (status) {
      case "AVAILABLE":
        return "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200";
      case "BORROWED":
        return "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200";
      case "RESERVED":
        return "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200";
      case "DAMAGED":
        return "bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200";
      case "LOST":
        return "bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200";
      default:
        return "bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200";
    }
  };

  /**
   * Etykiety statusów po polsku.
   */
  const getStatusLabel = (status: string) => {
    switch (status) {
      case "AVAILABLE":
        return "Dostępny";
      case "BORROWED":
        return "Wypożyczony";
      case "RESERVED":
        return "Zarezerwowany";
      case "DAMAGED":
        return "Uszkodzony";
      case "LOST":
        return "Zgubiony";
      default:
        return status;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Nagłówek */}
        <div className="mb-8">
          <Button variant="outline" onClick={() => navigate("/librarian")} className="mb-4">
            ← Wróć do panelu
          </Button>

          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2 flex items-center gap-3">
                <Package size={32} />
                Zarządzanie egzemplarzami
              </h1>
              <p className="text-gray-600 dark:text-gray-400">
                Dodawaj i zarządzaj fizycznymi egzemplarzami książek
              </p>
            </div>
          </div>
        </div>

        {/* Formularz wyboru książki */}
        <div className="mb-6 bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
          <form onSubmit={handleBookIdChange}>
            <div className="flex gap-4">
              <div className="flex-1">
                <Input
                  label="ID książki"
                  type="text"
                  value={selectedBookId}
                  onChange={(e) => setSelectedBookId(e.target.value)}
                  placeholder="Wprowadź UUID książki"
                  required
                  fullWidth
                />
              </div>
              <div className="flex items-end">
                <Button type="submit" variant="primary">
                  Załaduj egzemplarze
                </Button>
              </div>
            </div>
          </form>
        </div>

        {/* Przycisk dodaj egzemplarz (F16) */}
        {selectedBookId && (
          <div className="mb-6">
            <Button variant="primary" onClick={handleAddCopy} className="flex items-center gap-2">
              <Plus size={20} />
              Dodaj nowy egzemplarz
            </Button>
          </div>
        )}

        {/* Loading state */}
        {isLoading && <Loading text="Ładowanie egzemplarzy..." />}

        {/* Error state */}
        {error && !isLoading && (
          <div className="rounded-md bg-red-50 dark:bg-red-900/20 p-4 border border-red-200 dark:border-red-800">
            <div className="flex">
              <AlertCircle className="h-5 w-5 text-red-400" />
              <div className="ml-3">
                <p className="text-sm text-red-800 dark:text-red-200">{error}</p>
              </div>
            </div>
          </div>
        )}

        {/* Brak egzemplarzy */}
        {!isLoading && !error && selectedBookId && copies.length === 0 && (
          <div className="text-center py-12 bg-white dark:bg-gray-800 rounded-lg shadow-md">
            <Package size={48} className="mx-auto text-gray-400 mb-4" />
            <p className="text-gray-600 dark:text-gray-400 text-lg mb-2">
              Brak egzemplarzy dla tej książki
            </p>
            <Button variant="primary" onClick={handleAddCopy} className="mt-4">
              Dodaj pierwszy egzemplarz
            </Button>
          </div>
        )}

        {/* Lista egzemplarzy */}
        {!isLoading && !error && copies.length > 0 && (
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md overflow-hidden">
            <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
                Egzemplarze ({copies.length})
              </h2>
            </div>

            <div className="divide-y divide-gray-200 dark:divide-gray-700">
              {copies.map((copy) => (
                <div
                  key={copy.id}
                  className="p-6 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-4 mb-2">
                        <span className="text-lg font-semibold text-gray-900 dark:text-white">
                          {copy.inventory_no}
                        </span>
                        <span
                          className={`px-2 py-1 text-xs rounded-full ${getStatusColor(
                            copy.status
                          )}`}
                        >
                          {getStatusLabel(copy.status)}
                        </span>
                      </div>

                      <div className="flex items-center gap-4 text-sm text-gray-600 dark:text-gray-400">
                        {copy.location && (
                          <div className="flex items-center gap-1">
                            <MapPin size={16} />
                            <span>{copy.location}</span>
                          </div>
                        )}
                        <span>ID: {copy.id}</span>
                      </div>
                    </div>

                    <div className="flex gap-2">
                      <button
                        onClick={() => handleEditCopy(copy.id)}
                        className="p-2 text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300"
                        title="Edytuj egzemplarz"
                      >
                        <Edit size={20} />
                      </button>
                      <button
                        onClick={() => handleDeleteCopy(copy.id)}
                        className="p-2 text-red-600 hover:text-red-800 dark:text-red-400 dark:hover:text-red-300"
                        title="Usuń egzemplarz"
                      >
                        <Trash2 size={20} />
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Instrukcja */}
        {!selectedBookId && (
          <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4 border border-blue-200 dark:border-blue-800">
            <div className="flex">
              <AlertCircle className="h-5 w-5 text-blue-400" />
              <div className="ml-3">
                <p className="text-sm text-blue-800 dark:text-blue-200">
                  <span className="font-semibold">Jak zacząć:</span>
                </p>
                <ul className="text-xs text-blue-700 dark:text-blue-300 mt-2 space-y-1 list-disc list-inside">
                  <li>Wprowadź UUID książki w formularzu powyżej</li>
                  <li>Kliknij "Załaduj egzemplarze" aby zobaczyć istniejące egzemplarze</li>
                  <li>Dodaj nowe egzemplarze używając przycisku "Dodaj nowy egzemplarz"</li>
                  <li>Każdy egzemplarz ma unikalny numer inwentarzowy</li>
                </ul>
              </div>
            </div>
          </div>
        )}

        {/* Informacja o przyszłych funkcjach */}
        <div className="mt-8 bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4 border border-blue-200 dark:border-blue-800">
          <div className="flex">
            <AlertCircle className="h-5 w-5 text-blue-400" />
            <div className="ml-3">
              <p className="text-sm text-blue-800 dark:text-blue-200">
                <span className="font-semibold">W przygotowaniu:</span>
              </p>
              <ul className="text-xs text-blue-700 dark:text-blue-300 mt-2 space-y-1 list-disc list-inside">
                <li>Formularz dodawania nowych egzemplarzy (F16)</li>
                <li>Edycja statusu i lokalizacji egzemplarzy</li>
                <li>Usuwanie egzemplarzy z systemu</li>
                <li>Generowanie kodów kreskowych dla egzemplarzy</li>
                <li>Import wielu egzemplarzy jednocześnie</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ManageCopies;
