const tokenKey = "DASHBOARD_JWT_TOKEN"

export class UnauthenticatedException extends Error {
    constructor(message: string) {
        super(message);
        this.name = this.constructor.name;
    }
}

/**
 * Gets the saved token from local storage. Throws an UnauthenticatedException if no token is found.
 */
export function getSavedToken(): string {
    const token = localStorage.getItem(tokenKey);

    if (!token)
        throw new UnauthenticatedException("No token found, user is not authenticated");

    return token;
}

/**
 * Saves the given token in local storage for future authenticated requests.
 */
export function saveToken(token: string): void {
    localStorage.setItem(tokenKey, token);
}

/**
 * Clears any saved token from local storage, effectively logging the user out.
 */
export function clearToken(): void {
    localStorage.removeItem(tokenKey);
}

/**
 * Gets whether a token is saved in local storage.
 */
export function isTokenSaved(): boolean {
    const token = localStorage.getItem(tokenKey);
    return !!token;
}
