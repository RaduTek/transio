import { useState } from "react";
import { ScrollView, View } from "react-native";
import {
  Appbar,
  Button,
  Card,
  Chip,
  List,
  Searchbar,
  Text,
  useTheme,
} from "react-native-paper";

interface TransitRoute {
  id: string;
  number: string;
  name: string;
  status: "on-time" | "delayed" | "cancelled";
  stops: number;
  nextDeparture: string;
  color: string;
}

const ROUTES: TransitRoute[] = [
  {
    id: "1",
    number: "101",
    name: "Downtown Express",
    status: "on-time",
    stops: 12,
    nextDeparture: "5 min",
    color: "#FF6B6B",
  },
  {
    id: "2",
    number: "205",
    name: "Airport Connector",
    status: "on-time",
    stops: 8,
    nextDeparture: "12 min",
    color: "#4ECDC4",
  },
  {
    id: "3",
    number: "310",
    name: "Waterfront Loop",
    status: "delayed",
    stops: 15,
    nextDeparture: "18 min",
    color: "#45B7D1",
  },
  {
    id: "4",
    number: "415",
    name: "University Shuttle",
    status: "on-time",
    stops: 10,
    nextDeparture: "3 min",
    color: "#FFA07A",
  },
  {
    id: "5",
    number: "520",
    name: "Suburban Express",
    status: "cancelled",
    stops: 20,
    nextDeparture: "Cancelled",
    color: "#9B59B6",
  },
  {
    id: "6",
    number: "615",
    name: "Industrial District",
    status: "on-time",
    stops: 9,
    nextDeparture: "8 min",
    color: "#F39C12",
  },
];

export default function RoutesScene() {
  const theme = useTheme();
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedStatus, setSelectedStatus] = useState<string | null>(null);

  const filteredRoutes = ROUTES.filter((route) => {
    const matchesSearch =
      route.number.includes(searchQuery) ||
      route.name.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesStatus = !selectedStatus || route.status === selectedStatus;
    return matchesSearch && matchesStatus;
  });

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "on-time":
        return "check-circle";
      case "delayed":
        return "clock-alert";
      case "cancelled":
        return "close-circle";
      default:
        return "information";
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "on-time":
        return "#4CAF50";
      case "delayed":
        return "#FF9800";
      case "cancelled":
        return "#F44336";
      default:
        return theme.colors.primary;
    }
  };

  return <>
    <Appbar.Header>
      <Appbar.Content title="Transit Routes" />
    </Appbar.Header>
    <ScrollView style={{ flex: 1, backgroundColor: theme.colors.background }}>
      {/* Header */}
      <View style={{ padding: 16, paddingBottom: 0 }}>

        {/* Search Bar */}
        <Searchbar
          placeholder="Search route number or name"
          onChangeText={setSearchQuery}
          value={searchQuery}
          style={{ marginBottom: 16 }}
        />

        {/* Status Filters */}
        <View style={{ flexDirection: "row", flexWrap: "wrap", gap: 8, marginBottom: 16 }}>
          <Chip
            selected={selectedStatus === null}
            onPress={() => setSelectedStatus(null)}
            icon="tune"
          >
            All Routes
          </Chip>
          <Chip
            selected={selectedStatus === "on-time"}
            onPress={() => setSelectedStatus("on-time")}
            icon="check-circle"
          >
            On Time
          </Chip>
          <Chip
            selected={selectedStatus === "delayed"}
            onPress={() => setSelectedStatus("delayed")}
            icon="clock-alert"
          >
            Delayed
          </Chip>
          <Chip
            selected={selectedStatus === "cancelled"}
            onPress={() => setSelectedStatus("cancelled")}
            icon="close-circle"
          >
            Cancelled
          </Chip>
        </View>
      </View>

      {/* Routes List */}
      <View style={{ paddingHorizontal: 16 }}>
        {filteredRoutes.length > 0 ? (
          filteredRoutes.map((route) => (
            <Card
              key={route.id}
              style={{
                marginBottom: 12,
                backgroundColor: theme.colors.surface,
              }}
            >
              <Card.Content>
                <View style={{ flexDirection: "row", alignItems: "center", gap: 12 }}>
                  {/* Route Number Badge */}
                  <View
                    style={{
                      width: 50,
                      height: 50,
                      borderRadius: 25,
                      backgroundColor: route.color,
                      justifyContent: "center",
                      alignItems: "center",
                    }}
                  >
                    <Text
                      variant="titleMedium"
                      style={{ fontWeight: "bold", color: "#fff" }}
                    >
                      {route.number}
                    </Text>
                  </View>

                  {/* Route Details */}
                  <View style={{ flex: 1 }}>
                    <Text variant="titleMedium" style={{ fontWeight: "bold" }}>
                      {route.name}
                    </Text>
                    <Text
                      variant="bodySmall"
                      style={{ color: theme.colors.onSurfaceVariant, marginTop: 4 }}
                    >
                      {route.stops} stops
                    </Text>
                  </View>

                  {/* Status Indicator */}
                  <View style={{ alignItems: "center" }}>
                    <List.Icon
                      icon={getStatusIcon(route.status)}
                      color={getStatusColor(route.status)}
                    />
                    <Text
                      variant="bodySmall"
                      style={{
                        color: getStatusColor(route.status),
                        marginTop: 4,
                        fontWeight: "bold",
                      }}
                    >
                      {route.nextDeparture}
                    </Text>
                  </View>
                </View>
              </Card.Content>
              <Card.Actions>
                <Button>View Details</Button>
                <Button mode="contained">Track Route</Button>
              </Card.Actions>
            </Card>
          ))
        ) : (
          <Card style={{ backgroundColor: theme.colors.surface, marginBottom: 12 }}>
            <Card.Content style={{ alignItems: "center", paddingVertical: 32 }}>
              <Text variant="titleMedium">No routes found</Text>
              <Text variant="bodyMedium" style={{ color: theme.colors.onSurfaceVariant }}>
                Try adjusting your search filters
              </Text>
            </Card.Content>
          </Card>
        )}
      </View>

      {/* Footer Info */}
      <Card style={{ margin: 16, backgroundColor: theme.colors.surfaceVariant }}>
        <Card.Content>
          <Text variant="labelMedium" style={{ fontWeight: "bold", marginBottom: 8 }}>
            Legend
          </Text>
          <View style={{ gap: 6 }}>
            <View style={{ flexDirection: "row", alignItems: "center", gap: 8 }}>
              <List.Icon icon="check-circle" color="#4CAF50" />
              <Text variant="bodySmall">On Time</Text>
            </View>
            <View style={{ flexDirection: "row", alignItems: "center", gap: 8 }}>
              <List.Icon icon="clock-alert" color="#FF9800" />
              <Text variant="bodySmall">Delayed</Text>
            </View>
            <View style={{ flexDirection: "row", alignItems: "center", gap: 8 }}>
              <List.Icon icon="close-circle" color="#F44336" />
              <Text variant="bodySmall">Cancelled</Text>
            </View>
          </View>
        </Card.Content>
      </Card>
    </ScrollView>
  </>;
}