# Prosta bezpieczna aplikacja internetowa

## Funkcjonalnośći
### 1. Moduł logowania wykorzystujący bazę SQLite
* Możliwość utworzenia nowego konta.
* Możliwość zalogowania.
* Możliwość zmiany hasła użytkownika.

## Zastosowane zabezpieczenia
### 1. Hasła chronione funkcją hash i solą
~~~~
hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'), salt, 100000)
~~~~
Hasła przechowywane są w bazie danych w formie hasha.
Aplikacja wykorzystuje popularną funkcję pbkdf2_hmac() z biblioteki hashlib, jej zaletą nad zwykłymi funkcjami skrótu jest jej wolne działanie. 
Funkcja wykorzystuje algrytm **SHA512**.
Do funkcji jest także przekazywana 60 bajtowa sól, generowana za każdym razem za pomocą funkcji **os.urandom()**, przeznaczonej do zastosowań kryptograficznych.
Ustalona jest także ilość iteracji hashowania na **100000**.

### 2. Weryfikacja danych z formularzów
Do weryfikacji danych wykorzystane zostały wyrażenia regularne.
W aplikacji wyróżnione zostały dwa typy danych od użytkownika: email i hasło.

Email
~~~~
^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$
~~~~
Restrykcyjne ograniczenia znaków podczas podawania emaila, werifikacja formatu adresu email.

Hasło
~~~~
^[!-~]*$
~~~~
Ograniczono dostępne znaki do zakesu ASCII 33-126. 

### 3. Zastosowanie ORM z SQLAlchemy
W aplikacji nie są bezpośrednio tworzone zapytania do bazy w języku SQL. Uniemożliwia to popełnienie prostego błędu w zapytaniu SQL. Mimo to wszystkie wejścia są weryfikowane.

### 4. Oczekiwanie 3 sekund po nieudanej próbie logowania
Jeżeli użytkownik podał złe hasło, możliwość podania nowego hasła jest wstrzymywana na czas trzech sekund.

### 5. Wymagane stare hasło przy jego zmianie
Aby użytkownik wejść w formularz zmiany hasła wymagane jest jego zalogowanie. Dodatkowo podając nowe hasło użytkownik musi podać aktualne hasło, którego weryfikacja jest warunkiem koniecznym zmiany hasła.

### 6. Cisteczka sesyjne niedostępne z poziomu javascriptu
Zastowany mechanizm sesji Flask Session automatycznie ustawia flagę ciastaczek sesyjnych HttpOnly. 

## Problemy
### 1. Nieszyfrowowane cisteczka sesyjne
Z powodu nie uruchomienia aplikacji poprzez serwer produkcyjny Apache i braku certyfikatu nie można było użyć szyfrowanych ciasteczek.
~~~~
app.config['SESSION_COOKIE_SECURE'] = False  # Should be True
~~~~
