import { useState, useEffect } from "react";
import { ScrollView, View } from "react-native";
import { Appbar, Card, ActivityIndicator, Text, useTheme, List, IconButton } from "react-native-paper";
import { useQuery } from "@tanstack/react-query";
import { useLocalSearchParams, useRouter } from "expo-router";
import { fetchApi } from "@/helpers/net";
import type { TransitRoute, TransitSubRoute, TransitStop, TransitSubRouteStop } from "@/types/transit";

interface SubRouteStopDetails extends TransitSubRouteStop {
    stop: TransitStop;
}

export default function RouteDetailsPage() {
    const theme = useTheme();
    const router = useRouter();
    const { route_id } = useLocalSearchParams<{ route_id: string }>();
    const [selectedSubRouteIndex, setSelectedSubRouteIndex] = useState(0);

    // Fetch route information
    const { data: route, isLoading: routeLoading } = useQuery({
        queryKey: ["route", route_id],
        queryFn: async () => {
            const response = await fetchApi(`/public/routes/${route_id}`);
            return response.json() as Promise<TransitRoute>;
        },
        enabled: !!route_id,
    });

    // Fetch subroutes
    const { data: subRoutes = [], isLoading: subRoutesLoading } = useQuery({
        queryKey: ["route-subroutes", route_id],
        queryFn: async () => {
            const response = await fetchApi(`/public/routes/${route_id}/subroutes`);
            return response.json() as Promise<TransitSubRoute[]>;
        },
        enabled: !!route_id,
    });

    // Get the currently selected subroute
    const selectedSubRoute = subRoutes[selectedSubRouteIndex];

    // Fetch stops for the selected subroute
    const { data: stops = [], isLoading: stopsLoading } = useQuery({
        queryKey: ["subroute-stops", selectedSubRoute?.id],
        queryFn: async () => {
            if (!selectedSubRoute?.id) return [];
            const response = await fetchApi(`/public/subroutes/${selectedSubRoute.id}/stops`);
            return response.json() as Promise<SubRouteStopDetails[]>;
        },
        enabled: !!selectedSubRoute?.id,
    });

    // Reset to first subroute when subroutes change
    useEffect(() => {
        if (subRoutes.length > 0 && selectedSubRouteIndex >= subRoutes.length) {
            setSelectedSubRouteIndex(0);
        }
    }, [subRoutes, selectedSubRouteIndex]);

    const toggleDirection = () => {
        if (subRoutes.length > 0) {
            setSelectedSubRouteIndex((prev) => (prev + 1) % subRoutes.length);
        }
    };

    const isLoading = routeLoading || subRoutesLoading;

    return (
        <>
            <Appbar.Header>
                <Appbar.BackAction onPress={() => router.back()} />
                <Appbar.Content 
                    title={route?.name || "Route Details"} 
                    subtitle={route?.code ? `Route ${route.code}` : undefined}
                />
                {subRoutes.length > 1 && (
                    <Appbar.Action 
                        icon="swap-vertical" 
                        onPress={toggleDirection}
                        disabled={isLoading}
                    />
                )}
            </Appbar.Header>
            <ScrollView style={{ flex: 1, backgroundColor: theme.colors.background }}>
                {isLoading ? (
                    <View style={{ justifyContent: "center", alignItems: "center", height: 200 }}>
                        <ActivityIndicator animating size="large" />
                    </View>
                ) : (
                    <>

                        {/* Subroute Direction Card */}
                        {selectedSubRoute && (
                            <Card style={{ margin: 16, backgroundColor: theme.colors.primaryContainer }}>
                                <Card.Content>
                                    <View style={{ flexDirection: "row", alignItems: "center", justifyContent: "space-between" }}>
                                        <View style={{ flex: 1 }}>
                                            <Text variant="titleMedium" style={{ fontWeight: "bold" }}>
                                                {selectedSubRoute.name}
                                            </Text>
                                            <Text variant="bodySmall" style={{ color: theme.colors.onSurfaceVariant, marginTop: 4 }}>
                                                {selectedSubRoute.code}
                                            </Text>
                                            {selectedSubRoute.description && (
                                                <Text variant="bodySmall" style={{ marginTop: 4 }}>
                                                    {selectedSubRoute.description}
                                                </Text>
                                            )}
                                        </View>
                                    </View>
                                </Card.Content>
                            </Card>
                        )}

                        {/* Stops List */}
                        <View style={{ marginHorizontal: 16, marginBottom: 16 }}>
                            <Text variant="titleMedium" style={{ fontWeight: "bold", marginBottom: 12 }}>
                                Stops ({stops.length})
                            </Text>
                            
                            {stopsLoading ? (
                                <View style={{ justifyContent: "center", alignItems: "center", height: 100 }}>
                                    <ActivityIndicator animating size="small" />
                                </View>
                            ) : stops.length > 0 ? (
                                <Card style={{ backgroundColor: theme.colors.surface }}>
                                    {stops.map((stopDetails, index) => (
                                        <View key={stopDetails.id}>
                                            <List.Item
                                                title={stopDetails.stop.name}
                                                description={stopDetails.stop.address || `Lat: ${stopDetails.stop.lat}, Lon: ${stopDetails.stop.lon}`}
                                                left={(props) => (
                                                    <View style={{ justifyContent: "center", alignItems: "center", width: 40 }}>
                                                        <Text variant="titleMedium" style={{ fontWeight: "bold", color: theme.colors.primary }}>
                                                            {stopDetails.stop_order}
                                                        </Text>
                                                    </View>
                                                )}
                                                right={(props) => <List.Icon {...props} icon="timer-sand" />}
                                            />
                                        </View>
                                    ))}
                                </Card>
                            ) : (
                                <Card style={{ backgroundColor: theme.colors.surface }}>
                                    <Card.Content style={{ alignItems: "center", paddingVertical: 32 }}>
                                        <Text variant="titleMedium">No stops found</Text>
                                        <Text variant="bodyMedium" style={{ color: theme.colors.onSurfaceVariant, marginTop: 4 }}>
                                            This route has no stops configured
                                        </Text>
                                    </Card.Content>
                                </Card>
                            )}
                        </View>
                    </>
                )}
            </ScrollView>
        </>
    );
}
