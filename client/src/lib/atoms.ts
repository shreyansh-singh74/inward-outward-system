import { User } from "@/features/users/component/table";
import { atom } from "jotai";

export const userAtom = atom(null);
export const usersAtom = atom<User[]>([]);
