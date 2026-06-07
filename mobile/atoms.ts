import { atom, createStore } from "jotai";
import { atomWithStorage } from "jotai/utils";
import { Customer } from "./types";

export const atomStore = createStore();

export const customerAtom = atomWithStorage<Customer | null>("customerData", null);