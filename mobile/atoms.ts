import { atom, createStore } from "jotai";
import { atomWithStorage } from "jotai/utils";
import { ProfileData } from "./types/users";

export const atomStore = createStore();

export const profileDataAtom = atomWithStorage<ProfileData | null>("customerProfileData", null);