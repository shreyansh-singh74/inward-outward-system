import { User } from "@/features/users/component/table";
import { atom } from "jotai";
import { DocumentRecord } from "@/routes/_protected/";
export interface UserInterface {
  id: string;
  name: string;
  role: string;
  department: string;
}
export const userAtom = atom<UserInterface | null>(null);
export const usersAtom = atom<User[]>([]);
export const myApplicationsAtom = atom<DocumentRecord[] | null>(null);
export const turn_in_applicationAtom = atom<DocumentRecord[] | null>(null);
