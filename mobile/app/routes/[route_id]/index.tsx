import { useState, useEffect, useMemo } from "react";
import { ScrollView, View, StyleSheet } from "react-native";
import { Appbar, Card, ActivityIndicator, Text, useTheme, List, BottomNavigation, Icon } from "react-native-paper";
import MapView, { Marker, Polyline, PROVIDER_GOOGLE } from "react-native-maps";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useLocalSearchParams, useRouter } from "expo-router";
import { fetchApi } from "@/helpers/net";
import type { TransitRoute, TransitSubRoute, TransitStop, TransitSubRouteStop } from "@/types/transit";

interface SubRouteStopDetails extends TransitSubRouteStop {
    stop: TransitStop;
}

interface SubRouteVehicle {
    shift_id: string;
    vehicle_id: string;
    lat: number;
    lon: number;
    speed_kmph?: number;
    heading_degrees?: number;
    timestamp: string;
}

const DEFAULT_REGION = {
    latitude: 45.7461,
    longitude: 21.2218,
    latitudeDelta: 0.1,
    longitudeDelta: 0.1,
};

const SCENE_ROUTES = [
    { key: "stops", title: "Stops", focusedIcon: "format-list-bulleted" },
    { key: "map", title: "Map", focusedIcon: "map" },
];

const styles = StyleSheet.create({
    stopMarker: {
        width: 14,
        height: 14,
        borderRadius: 7,
        backgroundColor: "#000",
        borderWidth: 2,
        borderColor: "#fff",
    },
    vehicleMarker: {
        backgroundColor: "#0d6efd",
        borderRadius: 20,
        padding: 6,
        borderWidth: 2,
        borderColor: "white",
        elevation: 4,
        shadowColor: "#000",
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.3,
        shadowRadius: 2,
    },
});

export default function RouteDetailsPage() {
    const theme = useTheme();
    const router = useRouter();
    const queryClient = useQueryClient();
    const { route_id } = useLocalSearchParams<{ route_id: string }>();
    const [selectedSubRouteIndex, setSelectedSubRouteIndex] = useState(0);
    const [sceneIndex, setSceneIndex] = useState(0);

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

    // Fetch active vehicles on the selected subroute
    const { data: vehicles = [] } = useQuery({
        queryKey: ["subroute-vehicles", selectedSubRoute?.id],
        queryFn: async () => {
            if (!selectedSubRoute?.id) return [];
            const response = await fetchApi(`/public/subroutes/${selectedSubRoute.id}/vehicles`);
            return response.json() as Promise<SubRouteVehicle[]>;
        },
        enabled: !!selectedSubRoute?.id,
        refetchInterval: 15_000,
    });

    // Reset to first subroute when subroutes change
    useEffect(() => {
        if (subRoutes.length > 0 && selectedSubRouteIndex >= subRoutes.length) {
            setSelectedSubRouteIndex(0);
        }
    }, [subRoutes, selectedSubRouteIndex]);

    const mapRegion = useMemo(() => {
        if (stops.length === 0) return DEFAULT_REGION;
        const lats = stops.map((s) => s.stop.lat);
        const lons = stops.map((s) => s.stop.lon);
        const minLat = Math.min(...lats);
        const maxLat = Math.max(...lats);
        const minLon = Math.min(...lons);
        const maxLon = Math.max(...lons);
        return {
            latitude: (minLat + maxLat) / 2,
            longitude: (minLon + maxLon) / 2,
            latitudeDelta: Math.max((maxLat - minLat) * 1.4, 0.01),
            longitudeDelta: Math.max((maxLon - minLon) * 1.4, 0.01),
        };
    }, [stops]);

    const orderedStops = useMemo(() => {
        return [...stops].sort((a, b) => a.stop_order - b.stop_order);
    }, [stops]);

    const stopLineCoordinates = useMemo(() => {
        return orderedStops.map((stopDetails) => ({
            latitude: stopDetails.stop.lat,
            longitude: stopDetails.stop.lon,
        }));
    }, [orderedStops]);

    const toggleDirection = () => {
        if (subRoutes.length > 0) {
            setSelectedSubRouteIndex((prev) => (prev + 1) % subRoutes.length);
        }
    };

    const handleRefresh = () => {
        queryClient.invalidateQueries({ queryKey: ["route", route_id] });
        queryClient.invalidateQueries({ queryKey: ["route-subroutes", route_id] });
        if (selectedSubRoute?.id) {
            queryClient.invalidateQueries({ queryKey: ["subroute-stops", selectedSubRoute.id] });
            queryClient.invalidateQueries({ queryKey: ["subroute-vehicles", selectedSubRoute.id] });
        }
    };

    const isLoading = routeLoading || subRoutesLoading;

    const renderScene = ({ route }: { route: { key: string } }) => {
        switch (route.key) {
            case "stops":
                return (
                    <ScrollView style={{ flex: 1, backgroundColor: theme.colors.background }}>
                        {/* Subroute Direction Card */}
                        {selectedSubRoute && (
                            <Card style={{ margin: 16, marginBottom: 0, backgroundColor: theme.colors.primaryContainer }}>
                                <Card.Content>
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
                                </Card.Content>
                            </Card>
                        )}
                        
                        <View style={{ marginHorizontal: 16, marginVertical: 16 }}>
                            <Text variant="titleMedium" style={{ fontWeight: "bold", marginBottom: 12 }}>
                                Stops ({stops.length})
                            </Text>
                            {stopsLoading ? (
                                <View style={{ justifyContent: "center", alignItems: "center", height: 100 }}>
                                    <ActivityIndicator animating size="small" />
                                </View>
                            ) : stops.length > 0 ? (
                                <Card style={{ backgroundColor: theme.colors.surface }}>
                                    {stops.map((stopDetails) => (
                                        <View key={stopDetails.id}>
                                            <List.Item
                                                title={stopDetails.stop.name}
                                                left={() => (
                                                    <View style={{ justifyContent: "center", alignItems: "center", width: 40 }}>
                                                        <Text variant="titleMedium" style={{ fontWeight: "bold", color: theme.colors.primary }}>
                                                            {stopDetails.stop_order + 1}
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
                    </ScrollView>
                );
            case "map":
                return (
                    <View style={{ flex: 1 }}>
                        {stopsLoading ? (
                            <View style={{ flex: 1, justifyContent: "center", alignItems: "center" }}>
                                <ActivityIndicator animating size="large" />
                            </View>
                        ) : (
                            <MapView
                                style={StyleSheet.absoluteFillObject}
                                initialRegion={mapRegion}
                                provider={PROVIDER_GOOGLE}
                            >
                                {stopLineCoordinates.length > 1 && (
                                    <Polyline
                                        coordinates={stopLineCoordinates}
                                        strokeColor="#000"
                                        strokeWidth={3}
                                    />
                                )}
                                {orderedStops.map((stopDetails) => (
                                    <Marker
                                        key={stopDetails.id}
                                        coordinate={{
                                            latitude: stopDetails.stop.lat,
                                            longitude: stopDetails.stop.lon,
                                        }}
                                        title={stopDetails.stop.name}
                                        description={stopDetails.stop.description || stopDetails.stop.address}
                                        anchor={{ x: 0.5, y: 0.5 }}
                                    >
                                        <View style={styles.stopMarker} />
                                    </Marker>
                                ))}
                                {vehicles.map((vehicle) => (
                                    <Marker
                                        key={vehicle.vehicle_id}
                                        coordinate={{
                                            latitude: vehicle.lat,
                                            longitude: vehicle.lon,
                                        }}
                                        title={`Vehicle ${vehicle.vehicle_id.slice(0, 8)}`}
                                        description={vehicle.speed_kmph != null ? `${vehicle.speed_kmph.toFixed(0)} km/h` : undefined}
                                        anchor={{ x: 0.5, y: 0.5 }}
                                    >
                                        <View style={styles.vehicleMarker}>
                                            <Icon source="bus" size={18} color="#fff" />
                                        </View>
                                    </Marker>
                                ))}
                            </MapView>
                        )}
                    </View>
                );
            default:
                return null;
        }
    };

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
                <Appbar.Action
                    icon="refresh"
                    onPress={handleRefresh}
                    disabled={isLoading}
                />
            </Appbar.Header>

            {isLoading ? (
                <View style={{ flex: 1, justifyContent: "center", alignItems: "center" }}>
                    <ActivityIndicator animating size="large" />
                </View>
            ) : (
                <View style={{ flex: 1 }}>
                    <BottomNavigation
                        navigationState={{ index: sceneIndex, routes: SCENE_ROUTES }}
                        onIndexChange={setSceneIndex}
                        renderScene={renderScene}
                    />
                </View>
            )}
        </>
    );
}
