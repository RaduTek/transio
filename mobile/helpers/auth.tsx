import * as SecureStore from "expo-secure-store"

const tokenKey = "MOBILE_JWT_TOKEN"
const tokenOptions : SecureStore.SecureStoreOptions = {
    requireAuthentication: false,
}

export class UnauthenticatedException extends Error {
    constructor(message: string) {
        super(message);
        this.name = this.constructor.name;
    }
}

/**
 * Gets the saved token from secure storage. Throws an UnauthenticatedException if no token is found.
 */
export async function getSavedTokenAsync() : Promise<string> {
    const token = await SecureStore.getItemAsync(tokenKey, tokenOptions);

    if (!token)
        throw new UnauthenticatedException("No token found, user is not authenticated");

    return token;
}

/**
 * Saves the given token in secure storage for future authenticated requests.
 */
export async function saveToken(token: string) {
    await SecureStore.setItemAsync(tokenKey, token, tokenOptions);
}

/**
 * Clears any saved token from secure storage, effectively logging the user out.
 */
export async function clearToken() {
    await SecureStore.setItemAsync(tokenKey, "", tokenOptions);
}

/**
 * Gets whether a token is saved in secure storage.
 */
export async function isTokenSaved() : Promise<boolean> {
    const token = await SecureStore.getItemAsync(tokenKey, tokenOptions);
    return !!token;
}
