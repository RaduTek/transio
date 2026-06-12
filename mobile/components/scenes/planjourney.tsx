import { useMemo, useState } from "react";
import { ScrollView, View, Pressable } from "react-native";
import {
    Appbar,
    Button,
    Card,
    ActivityIndicator,
    Searchbar,
    Text,
    IconButton,
    useTheme,
    Divider,
} from "react-native-paper";
import { useMutation, useQuery } from "@tanstack/react-query";
import { fetchApi, fetchWithAuth, postJSON } from "@/helpers/net";
import type { TransitRoute, TransitStop } from "@/types/transit";

const MAX_STOPS = 5;
const MIN_STOPS = 2;

interface JourneyLeg {
    route_id: string;
    board_stop_id: string;
    alight_stop_id: string;
}

interface PlanJourneyResponse {
    legs: JourneyLeg[];
}

interface StopRow {
    key: string;
    stopId: string | null;
    query: string;
}

function makeRow(seed: number): StopRow {
    return { key: `row-${seed}-${Math.random().toString(36).slice(2, 8)}`, stopId: null, query: "" };
}

export default function PlanJourneyScene() {
    const theme = useTheme();

    const [rows, setRows] = useState<StopRow[]>(() => [makeRow(0), makeRow(1)]);
    const [activeRowKey, setActiveRowKey] = useState<string | null>(null);

    const { data: stops = [], isLoading: stopsLoading } = useQuery({
        queryKey: ["stops"],
        queryFn: async () => {
            const res = await fetchApi("/public/stops");
            return (await res.json()) as TransitStop[];
        },
    });

    const { data: routes = [] } = useQuery({
        queryKey: ["transit-routes-all"],
        queryFn: async () => {
            const res = await fetchApi("/public/routes");
            return (await res.json()) as TransitRoute[];
        },
    });

    const stopsById = useMemo(() => {
        const m = new Map<string, TransitStop>();
        for (const s of stops) m.set(s.id, s);
        return m;
    }, [stops]);

    const routesById = useMemo(() => {
        const m = new Map<string, TransitRoute>();
        for (const r of routes) m.set(r.id, r);
        return m;
    }, [routes]);

    const planMutation = useMutation({
        mutationFn: async (stopIds: string[]) => {
            const res = await fetchWithAuth("/mobile/plan_journey", postJSON({ stop_ids: stopIds }));
            if (!res.ok) {
                const txt = await res.text();
                throw new Error(`Plan failed (${res.status}): ${txt}`);
            }
            return (await res.json()) as PlanJourneyResponse;
        },
    });

    const updateRow = (key: string, patch: Partial<StopRow>) => {
        setRows((prev) => prev.map((r) => (r.key === key ? { ...r, ...patch } : r)));
    };

    const addIntermediate = () => {
        if (rows.length >= MAX_STOPS) return;
        setRows((prev) => {
            const next = [...prev];
            next.splice(next.length - 1, 0, makeRow(next.length));
            return next;
        });
    };

    const removeRow = (key: string) => {
        if (rows.length <= MIN_STOPS) return;
        setRows((prev) => prev.filter((r) => r.key !== key));
        if (activeRowKey === key) setActiveRowKey(null);
    };

    const selectStop = (key: string, stop: TransitStop) => {
        updateRow(key, { stopId: stop.id, query: stop.name });
        setActiveRowKey(null);
    };

    const clearStop = (key: string) => {
        updateRow(key, { stopId: null, query: "" });
    };

    const allSelected = rows.every((r) => !!r.stopId);
    const uniqueStops = new Set(rows.map((r) => r.stopId).filter(Boolean)).size === rows.length;

    const onPlan = () => {
        if (!allSelected || !uniqueStops) return;
        planMutation.mutate(rows.map((r) => r.stopId as string));
    };

    const labelFor = (index: number) => {
        if (index === 0) return "Start";
        if (index === rows.length - 1) return "Destination";
        return `Stop ${index}`;
    };

    const iconFor = (index: number) => {
        if (index === 0) return "map-marker-radius";
        if (index === rows.length - 1) return "flag-checkered";
        return "map-marker";
    };

    const suggestionsFor = (row: StopRow): TransitStop[] => {
        const q = row.query.trim().toLowerCase();
        const usedIds = new Set(rows.filter((r) => r.key !== row.key && r.stopId).map((r) => r.stopId as string));
        const base = stops.filter((s) => !usedIds.has(s.id));
        if (!q) return base.slice(0, 8);
        return base
            .filter(
                (s) =>
                    s.name.toLowerCase().includes(q) ||
                    (s.address ?? "").toLowerCase().includes(q),
            )
            .slice(0, 8);
    };

    return (
        <>
            <Appbar.Header>
                <Appbar.Content title="Plan Journey" />
            </Appbar.Header>
            <ScrollView
                style={{ flex: 1, backgroundColor: theme.colors.background }}
                keyboardShouldPersistTaps="handled"
                contentContainerStyle={{ padding: 16, gap: 12 }}
            >
                {stopsLoading ? (
                    <View style={{ paddingVertical: 32, alignItems: "center" }}>
                        <ActivityIndicator animating size="large" />
                    </View>
                ) : (
                    <>
                        {rows.map((row, index) => {
                            const isActive = activeRowKey === row.key;
                            const suggestions = isActive ? suggestionsFor(row) : [];
                            return (
                                <Card key={row.key} style={{ backgroundColor: theme.colors.surface }}>
                                    <Card.Content style={{ gap: 8 }}>
                                        <View style={{ flexDirection: "row", alignItems: "center", justifyContent: "space-between" }}>
                                            <Text variant="labelLarge" style={{ color: theme.colors.onSurfaceVariant }}>
                                                {labelFor(index)}
                                            </Text>
                                            {index !== 0 && index !== rows.length - 1 && (
                                                <IconButton
                                                    icon="close"
                                                    size={18}
                                                    onPress={() => removeRow(row.key)}
                                                />
                                            )}
                                        </View>
                                        <Searchbar
                                            icon={iconFor(index)}
                                            placeholder="Search a stop..."
                                            value={row.query}
                                            onChangeText={(text) => {
                                                updateRow(row.key, { query: text, stopId: null });
                                                setActiveRowKey(row.key);
                                            }}
                                            onFocus={() => setActiveRowKey(row.key)}
                                            onClearIconPress={() => clearStop(row.key)}
                                        />
                                        {isActive && suggestions.length > 0 && (
                                            <View
                                                style={{
                                                    borderRadius: 8,
                                                    backgroundColor: theme.colors.surfaceVariant,
                                                }}
                                            >
                                                {suggestions.map((s, i) => (
                                                    <View key={s.id}>
                                                        {i > 0 && <Divider />}
                                                        <Pressable
                                                            onPress={() => selectStop(row.key, s)}
                                                            style={{ paddingHorizontal: 12, paddingVertical: 10 }}
                                                        >
                                                            <Text variant="bodyMedium" style={{ fontWeight: "600" }}>
                                                                {s.name}
                                                            </Text>
                                                            {s.address && (
                                                                <Text
                                                                    variant="bodySmall"
                                                                    style={{ color: theme.colors.onSurfaceVariant }}
                                                                >
                                                                    {s.address}
                                                                </Text>
                                                            )}
                                                        </Pressable>
                                                    </View>
                                                ))}
                                            </View>
                                        )}
                                    </Card.Content>
                                </Card>
                            );
                        })}

                        <View style={{ flexDirection: "row", gap: 8 }}>
                            <Button
                                mode="outlined"
                                icon="plus"
                                onPress={addIntermediate}
                                disabled={rows.length >= MAX_STOPS}
                                style={{ flex: 1 }}
                            >
                                Add stop
                            </Button>
                            <Button
                                mode="contained"
                                icon="routes"
                                onPress={onPlan}
                                disabled={!allSelected || !uniqueStops || planMutation.isPending}
                                loading={planMutation.isPending}
                                style={{ flex: 1 }}
                            >
                                Plan
                            </Button>
                        </View>

                        {!uniqueStops && allSelected && (
                            <Text style={{ color: theme.colors.error }}>
                                Each stop must be unique.
                            </Text>
                        )}

                        {planMutation.error && (
                            <Card style={{ backgroundColor: theme.colors.errorContainer }}>
                                <Card.Content>
                                    <Text style={{ color: theme.colors.onErrorContainer }}>
                                        {planMutation.error instanceof Error
                                            ? planMutation.error.message
                                            : "Failed to plan journey"}
                                    </Text>
                                </Card.Content>
                            </Card>
                        )}

                        {planMutation.data && (
                            <JourneyResult
                                legs={planMutation.data.legs}
                                stopsById={stopsById}
                                routesById={routesById}
                            />
                        )}
                    </>
                )}
            </ScrollView>
        </>
    );
}

interface JourneyResultProps {
    legs: JourneyLeg[];
    stopsById: Map<string, TransitStop>;
    routesById: Map<string, TransitRoute>;
}

function JourneyResult({ legs, stopsById, routesById }: JourneyResultProps) {
    const theme = useTheme();

    if (legs.length === 0) {
        return (
            <Card style={{ backgroundColor: theme.colors.surface }}>
                <Card.Content>
                    <Text>No journey legs were returned.</Text>
                </Card.Content>
            </Card>
        );
    }

    return (
        <View style={{ gap: 8 }}>
            <Text variant="titleMedium" style={{ marginTop: 8 }}>
                Your journey
            </Text>
            {legs.map((leg, i) => {
                const route = routesById.get(leg.route_id);
                const board = stopsById.get(leg.board_stop_id);
                const alight = stopsById.get(leg.alight_stop_id);
                return (
                    <Card key={i} style={{ backgroundColor: theme.colors.surface }}>
                        <Card.Content style={{ gap: 6 }}>
                            <View style={{ flexDirection: "row", alignItems: "center", gap: 8 }}>
                                <View
                                    style={{
                                        width: 28,
                                        height: 28,
                                        borderRadius: 14,
                                        backgroundColor: theme.colors.primary,
                                        justifyContent: "center",
                                        alignItems: "center",
                                    }}
                                >
                                    <Text style={{ color: theme.colors.onPrimary, fontWeight: "bold" }}>
                                        {i + 1}
                                    </Text>
                                </View>
                                <Text variant="titleSmall" style={{ flex: 1 }}>
                                    {route ? `Route ${route.code} — ${route.name}` : `Route ${leg.route_id}`}
                                </Text>
                            </View>
                            <View style={{ paddingLeft: 36, gap: 2 }}>
                                <Text variant="bodyMedium">
                                    Board at <Text style={{ fontWeight: "600" }}>{board?.name ?? leg.board_stop_id}</Text>
                                </Text>
                                <Text variant="bodyMedium">
                                    Hop off at <Text style={{ fontWeight: "600" }}>{alight?.name ?? leg.alight_stop_id}</Text>
                                </Text>
                            </View>
                        </Card.Content>
                    </Card>
                );
            })}
        </View>
    );
}
