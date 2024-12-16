import { Calendar, Home, Inbox, Search, Settings } from "lucide-react";

import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
} from "@/components/ui/sidebar";
import { useAtomValue } from "jotai";
import { userAtom } from "@/lib/atoms";
import { useEffect, useState } from "react";
import { Button } from "./ui/button";
import { router } from "@/main";
const items = [
  {
    title: "My applications",
    function: () => {
      router.navigate({ to: "/" });
    },
    icon: Home,
  },
  {
    title: "Turn in",
    function: () => {
      router.navigate({ to: "/turn_in" });
    },
    icon: Inbox,
  },
  {
    title: "Handed application",
    function: () => {
      router.navigate({ to: "/hand_in" });
    },
    icon: Calendar,
  },
  {
    title: "User",
    function: () => {
      router.navigate({ to: "/users" });
    },
    icon: Search,
  },
  {
    title: "Logout",
    function: async () => {
      const res = await fetch("/api/logout", {
        method: "POST",
      });
      router.navigate({ to: "/login" });
    },
    icon: Settings,
  },
];

export function AppSidebar() {
  const user = useAtomValue(userAtom);
  const [sideBarItems, setSideBarItems] = useState<typeof items | null>(null);
  useEffect(() => {
    const authoritiesOption = items.filter((item) => item.title !== "User");
    const studentOption = authoritiesOption.filter(
      (item) => item.title !== "Handed application"
    );
    if (user?.role === "student") {
      setSideBarItems(studentOption);
    } else if (user?.role === "system_admin") {
      setSideBarItems(items);
    } else {
      setSideBarItems(authoritiesOption);
    }
  }, [user]);
  return (
    <Sidebar>
      <SidebarContent className="bg-[#d17a00] text-white">
        <SidebarGroup>
          <SidebarGroupLabel className="text-white flex flex-col mb-16">
            <img src="/tcet_logo_2.png" />
          </SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {sideBarItems?.map((item) => (
                <SidebarMenuItem key={item.title}>
                  <SidebarMenuButton asChild>
                    <Button
                      onClick={item.function}
                      variant={"link"}
                      className="flex justify-start text-white"
                    >
                      <item.icon />
                      <span>{item.title}</span>
                    </Button>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>
    </Sidebar>
  );
}
