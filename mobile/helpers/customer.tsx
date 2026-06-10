import { atomStore, profileDataAtom } from "@/atoms";
import { ProfileData } from "@/types/users";
import { useAtomValue } from "jotai";
import { useEffect, useState } from "react";
import { fetchWithAuth } from "./net";

export async function fetchProfileData(): Promise<ProfileData> {
    const response = await fetchWithAuth('/mobile/profile/data');

    if (!response.ok) {
        console.log("fetchProfileData response:", response);
        throw new Error(response.body ? await response.text() : "Failed to fetch profile data");
    }

    const data: ProfileData = await response.json();
    return data;
}

export interface UseProfileDataResult {
    profile: ProfileData | null;
    loading: boolean;
    error: Error | null;
    loggedIn: boolean;
}

export function useProfileData(): UseProfileDataResult {
    const profile = useAtomValue(profileDataAtom);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<Error | null>(null);

    useEffect(() => {
        if (!profile) {
            setLoading(true);
            setError(null);
            (async () => {
                try {
                    const fetchedProfile = await fetchProfileData();
                    atomStore.set(profileDataAtom, fetchedProfile);
                } catch (error) {
                    if (error instanceof Error && error.name === "UnauthenticatedException") {
                        console.warn("User is not authenticated, cannot fetch profile data");
                    } else {
                        console.error("Error fetching profile data:", error);
                        setError(error instanceof Error ? error : new Error("An unknown error occurred"));
                    }
                    atomStore.set(profileDataAtom, null);
                }
                setLoading(false);
            })();
        }
    }, [profile]);

    return {profile, loading, error, loggedIn: !!profile?.customer?.id};
}