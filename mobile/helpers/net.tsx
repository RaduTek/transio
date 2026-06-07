import { getSavedTokenAsync } from "./auth";

const apiBaseUrl = process.env.EXPO_PUBLIC_MOBILE_API_URL || "http://localhost:8000/mobile";

export function fetchApi(endpoint: string, options?: RequestInit) : Promise<Response> {
    console.log(process.env);
    console.log(`Making API request to ${apiBaseUrl}${endpoint} with options:`, options);
    return fetch(`${apiBaseUrl}${endpoint}`, options);
}

export function fetchWithAuth(endpoint: string, options?: RequestInit) : Promise<Response> {
    return new Promise(async (resolve, reject) => {
        try {
            const token = await getSavedTokenAsync();
            const response = await fetch(`${apiBaseUrl}${endpoint}`, {
                ...(options || {}),
                headers: {
                    ...(options?.headers || {}),
                    'Authorization': `Bearer ${token}`
                }
            });
            resolve(response);
        } catch (error) {
            reject(error);
        }
    });
}

export function postJSON(data: any) : RequestInit {
    return {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    }
}