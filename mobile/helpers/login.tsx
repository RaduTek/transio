import { Customer } from "@/types/users";
import { fetchApi, postJSON } from "./net";
import { saveToken } from "./auth";
import { atomStore, profileDataAtom } from "@/atoms";

export interface LoginRequest {
    email: string;
    password: string;
}

export interface SignupRequest {
    email: string;
    phone: string;
    first_name: string;
    last_name: string;
    password: string;
}

export interface LoginResponse {
    customer: Customer;
    token: string;
}

export async function login(request: LoginRequest) {
    const response = await fetchApi('/mobile/login', postJSON(request));

    if (!response.ok) {
        throw new Error(response.body ? await response.text() : "Login failed");
    }

    const data: LoginResponse = await response.json();
    
    await saveToken(data.token);

    atomStore.set(profileDataAtom, data.customer);
}


export async function signup(request: SignupRequest) {
    const response = await fetchApi('/mobile/signup', postJSON(request));

    if (!response.ok) {
        throw new Error(response.body ? await response.text() : "Signup failed");
    }

    const data: LoginResponse = await response.json();

    await saveToken(data.token);

    atomStore.set(profileDataAtom, data.customer);
}