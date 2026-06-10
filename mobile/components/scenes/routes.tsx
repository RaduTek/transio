import { useState } from "react";
import { ScrollView, View, FlatList } from "react-native";
import { Appbar, Button, Card, ActivityIndicator, Searchbar, Text, useTheme } from "react-native-paper";
import { useQuery } from "@tanstack/react-query";
import { fetchApi } from "../../helpers/net";
import type { TransitCategory, TransitRoute } from "../../types";

const ROUTE_COLORS = [
    "#FF6B6B",
    "#4ECDC4",
    "#45B7D1",
    "#FFA07A",
    "#9B59B6",
    "#F39C12",
    "#3498DB",
    "#2ECC71",
    "#E74C3C",
    "#1ABC9C",
];

const getRouteColor = (code: string) => {
    const hash = code.split("").reduce((acc, char) => acc + char.charCodeAt(0), 0);
    return ROUTE_COLORS[hash % ROUTE_COLORS.length];
};

export default function RoutesScene() {
    const theme = useTheme();
    const [selectedCategoryId, setSelectedCategoryId] = useState<string | null>(null);
    const [searchQuery, setSearchQuery] = useState("");

    // Fetch categories
    const { data: categories = [], isLoading: categoriesLoading } = useQuery({
        queryKey: ["transit-categories"],
        queryFn: async () => {
            const response = await fetchApi("/public/categories");
            const data = await response.json();
            selectedCategoryId || setSelectedCategoryId(data[0]?.id || null);
            return data as TransitCategory[];
        },
    });

    // Fetch routes for selected category
    const { data: routes = [], isLoading: routesLoading } = useQuery({
        queryKey: ["transit-routes", selectedCategoryId],
        queryFn: async () => {
            if (!selectedCategoryId) return [];
            const response = await fetchApi(`/public/categories/${selectedCategoryId}/routes`);
            return response.json() as Promise<TransitRoute[]>;
        },
        enabled: !!selectedCategoryId,
    });

    const filteredRoutes = routes.filter((route) =>
        route.code.includes(searchQuery) || route.name.toLowerCase().includes(searchQuery.toLowerCase())
    );

    return (
        <>
            <Appbar.Header>
                <Appbar.Content title="Transit Routes" />
            </Appbar.Header>
            <ScrollView style={{ flex: 1, backgroundColor: theme.colors.background }}>
                {/* Categories Horizontal List */}
                <View style={{ paddingVertical: 12 }}>
                    {categoriesLoading ? (
                        <View style={{ paddingHorizontal: 16, justifyContent: "center", alignItems: "center", height: 50 }}>
                            <ActivityIndicator animating size="small" />
                        </View>
                    ) : categories.length > 0 ? (
                        <FlatList
                            data={categories}
                            horizontal
                            scrollEnabled={false}
                            contentContainerStyle={{ paddingHorizontal: 16, gap: 8 }}
                            renderItem={({ item }) => (
                                <Button
                                    mode={selectedCategoryId === item.id ? "contained" : "outlined"}
                                    onPress={() => setSelectedCategoryId(item.id)}
                                    style={{ marginVertical: 4 }}
                                >
                                    {item.name}
                                </Button>
                            )}
                            keyExtractor={(item) => item.id}
                        />
                    ) : null}
                </View>

                {/* Search Bar */}
                {selectedCategoryId && (
                    <View style={{ paddingHorizontal: 16, paddingBottom: 12 }}>
                        <Searchbar
                            placeholder="Search route code or name"
                            onChangeText={setSearchQuery}
                            value={searchQuery}
                        />
                    </View>
                )}

                {/* Routes List */}
                <View style={{ paddingHorizontal: 16 }}>
                    {!selectedCategoryId ? (
                        <Card style={{ backgroundColor: theme.colors.surface }}>
                            <Card.Content style={{ alignItems: "center", paddingVertical: 32 }}>
                                <Text variant="titleMedium">Select a category</Text>
                                <Text variant="bodyMedium" style={{ color: theme.colors.onSurfaceVariant, marginTop: 4 }}>
                                    Choose a transit category above to view routes
                                </Text>
                            </Card.Content>
                        </Card>
                    ) : routesLoading ? (
                        <View style={{ justifyContent: "center", alignItems: "center", height: 200 }}>
                            <ActivityIndicator animating size="large" />
                        </View>
                    ) : filteredRoutes.length > 0 ? (
                        filteredRoutes.map((route) => (
                            <Card
                                key={route.id}
                                style={{
                                    marginBottom: 12,
                                    backgroundColor: theme.colors.surface,
                                }}
                                onPress={() => {
                                    // TODO: Navigate to route details
                                    console.log("Tapped route:", route.id);
                                }}
                            >
                                <Card.Content>
                                    <View style={{ flexDirection: "row", alignItems: "center", gap: 12 }}>
                                        {/* Route Code Badge */}
                                        <View
                                            style={{
                                                width: 50,
                                                height: 50,
                                                borderRadius: 25,
                                                backgroundColor: getRouteColor(route.code),
                                                justifyContent: "center",
                                                alignItems: "center",
                                            }}
                                        >
                                            <Text variant="titleMedium" style={{ fontWeight: "bold", color: "#fff" }}>
                                                {route.code}
                                            </Text>
                                        </View>

                                        {/* Route Details */}
                                        <View style={{ flex: 1 }}>
                                            <Text variant="titleMedium" style={{ fontWeight: "bold" }}>
                                                {route.name}
                                            </Text>
                                        </View>
                                    </View>
                                </Card.Content>
                            </Card>
                        ))
                    ) : (
                        <Card style={{ backgroundColor: theme.colors.surface }}>
                            <Card.Content style={{ alignItems: "center", paddingVertical: 32 }}>
                                <Text variant="titleMedium">No routes found</Text>
                                <Text variant="bodyMedium" style={{ color: theme.colors.onSurfaceVariant, marginTop: 4 }}>
                                    Try adjusting your search query
                                </Text>
                            </Card.Content>
                        </Card>
                    )}
                </View>
            </ScrollView>
        </>
    );
}
