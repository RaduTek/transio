import { getSavedToken } from "./auth";

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || "/api";

export function fetchApi(endpoint: string, options?: RequestInit) : Promise<Response> {
    return fetch(`${apiBaseUrl}${endpoint}`, options);
}

export function fetchWithAuth(endpoint: string, options?: RequestInit) : Promise<Response> {
    const token = getSavedToken();
    return fetch(`${apiBaseUrl}${endpoint}`, {
        ...(options || {}),
        headers: {
            ...(options?.headers || {}),
            'Authorization': `Bearer ${token}`
        }
    });
}

export function postJSON(data: unknown) : RequestInit {
    return {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    }
}