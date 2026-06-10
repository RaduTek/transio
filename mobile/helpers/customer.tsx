import { atomStore, customerAtom } from "@/atoms";
import { Customer } from "@/types";
import { useAtomValue } from "jotai";
import { useEffect, useState } from "react";
import { fetchWithAuth } from "./net";

export async function fetchCustomer(): Promise<Customer> {
    const response = await fetchWithAuth('/profile/customerInfo');

    if (!response.ok) {
        throw new Error(response.body ? await response.text() : "Failed to fetch customer data");
    }

    const data: Customer = await response.json();
    return data;
}

export interface UseCustomerResult {
    customer: Customer | null;
    loading: boolean;
    error: Error | null;
    loggedIn: boolean;
}

export function useCustomer(): UseCustomerResult {
    const customer = useAtomValue(customerAtom);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<Error | null>(null);

    useEffect(() => {
        if (!customer) {
            setLoading(true);
            setError(null);
            (async () => {
                try {
                    const fetchedCustomer = await fetchCustomer();
                    atomStore.set(customerAtom, fetchedCustomer);
                } catch (error) {
                    if (error instanceof Error && error.name === "UnauthenticatedException") {
                        console.warn("User is not authenticated, cannot fetch customer data");
                    } else {
                        console.error("Error fetching customer data:", error);
                        setError(error instanceof Error ? error : new Error("An unknown error occurred"));
                    }
                    atomStore.set(customerAtom, null);
                }
                setLoading(false);
            })();
        }
    }, [customer]);

    return {customer, loading, error, loggedIn: !!customer?.id};
}