import { createFileRoute, useLoaderData } from "@tanstack/react-router";
import { toast } from "sonner";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useMemo, useState } from "react";
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Legend,
  Tooltip,
} from "recharts";
import { ChartContainer } from "@/components/ui/chart";
type DailyStats = {
  pending: number;
  accepted: number;
  rejected: number;
};

type StatsData = {
  [date: string]: DailyStats;
};

const COLORS = ["#0088FE", "#00C49F", "#FFBB28"];

export const Route = createFileRoute("/_protected/stats")({
  component: RouteComponent,
  loader: async () => {
    const res = await fetch("/api/application/get-stats/1", {
      method: "GET",
    });
    if (res.status != 200) {
      toast.error("Failed to load application");
      console.log(await res.json());
      return { error: "Failed to load application" };
    }
    const data = await res.json();
    const stats = data.stats as StatsData;
    return { stats };
  },
});

function RouteComponent() {
  const { error, stats: statsData } = useLoaderData({
    from: "/_protected/stats",
  });
  const [selectedYear, setSelectedYear] = useState<string>("all");
  const [selectedMonth, setSelectedMonth] = useState<string>("all");
  const [selectedDay, setSelectedDay] = useState<string>("all");
  console.log(statsData);
  const years = useMemo(() => {
    return [
      "all",
      ...new Set(
        Object.keys(statsData ?? {}).map((date) => date.split("-")[0])
      ),
    ];
  }, []);

  const months = useMemo(() => {
    if (selectedYear === "all") return ["all"];
    return [
      "all",
      ...new Set(
        Object.keys(statsData ?? {})
          .filter((date) => date.startsWith(selectedYear))
          .map((date) => date.split("-")[1])
      ),
    ];
  }, [selectedYear]);

  const days = useMemo(() => {
    if (selectedMonth === "all") return ["all"];
    return [
      "all",
      ...new Set(
        Object.keys(statsData ?? {})
          .filter((date) => date.startsWith(`${selectedYear}-${selectedMonth}`))
          .map((date) => date.split("-")[2])
      ),
    ];
  }, [selectedYear, selectedMonth]);

  const filteredData = useMemo(() => {
    return Object.entries(statsData ?? {}).reduce(
      (acc, [date, stats]) => {
        const [year, month, day] = date.split("-");
        if (
          (selectedYear === "all" || year === selectedYear) &&
          (selectedMonth === "all" || month === selectedMonth) &&
          (selectedDay === "all" || day === selectedDay)
        ) {
          Object.entries(stats).forEach(([status, count]) => {
            acc[status] = (acc[status] || 0) + count;
          });
        }
        return acc;
      },
      {} as Record<string, number>
    );
  }, [selectedYear, selectedMonth, selectedDay]);
  const chartData = useMemo(() => {
    return Object.entries(filteredData).map(([name, value]) => ({
      name,
      value,
    }));
  }, [filteredData]);

  return (
    <div className="w-[100dvw] lg:w-[80dvw]">
      {error ? (
        <h1 className="flex justify-center items-center">{error}</h1>
      ) : (
        <div>
          <Card className="w-full max-w-3xl mx-auto">
            <CardHeader>
              <CardTitle>Application Statistics</CardTitle>
              <CardDescription>
                Distribution of application statuses
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex space-x-4 mb-4">
                <Select value={selectedYear} onValueChange={setSelectedYear}>
                  <SelectTrigger className="w-[180px]">
                    <SelectValue placeholder="Select Year" />
                  </SelectTrigger>
                  <SelectContent>
                    {years.map((year) => (
                      <SelectItem key={year} value={year}>
                        {year === "all" ? "All Years" : year}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                <Select value={selectedMonth} onValueChange={setSelectedMonth}>
                  <SelectTrigger className="w-[180px]">
                    <SelectValue placeholder="Select Month" />
                  </SelectTrigger>
                  <SelectContent>
                    {months.map((month) => (
                      <SelectItem key={month} value={month}>
                        {month === "all"
                          ? "All Months"
                          : new Date(`2000-${month}-01`).toLocaleString(
                              "default",
                              { month: "long" }
                            )}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                <Select value={selectedDay} onValueChange={setSelectedDay}>
                  <SelectTrigger className="w-[180px]">
                    <SelectValue placeholder="Select Day" />
                  </SelectTrigger>
                  <SelectContent>
                    {days.map((day) => (
                      <SelectItem key={day} value={day}>
                        {day === "all" ? "All Days" : day}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <ChartContainer
                config={{
                  pending: {
                    label: "Pending",
                    color: COLORS[0],
                  },
                  accepted: {
                    label: "Accepted",
                    color: COLORS[1],
                  },
                  rejected: {
                    label: "Rejected",
                    color: COLORS[2],
                  },
                }}
                className="h-[300px]"
              >
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={chartData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {chartData.map((entry, index) => (
                        <Cell
                          key={`cell-${index}`}
                          fill={COLORS[index % COLORS.length]}
                        />
                      ))}
                    </Pie>
                    <Tooltip />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              </ChartContainer>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}
