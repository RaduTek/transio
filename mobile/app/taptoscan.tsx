import { useState, useEffect } from "react";
import { View, ScrollView, Animated } from "react-native";
import {
  Button,
  Card,
  Text,
  useTheme,
  List,
  Divider,
} from "react-native-paper";
import { useLocalSearchParams, useRouter } from "expo-router";
import { isExpoGoRuntime } from "@/helpers/hce";

export default function TapToScan() {
  const theme = useTheme();
  const router = useRouter();
  const params = useLocalSearchParams<{
    status?: "success" | "error";
    reason?: string;
  }>();
  const [scaleAnim] = useState(new Animated.Value(0));
  const [opacityAnim] = useState(new Animated.Value(0));
  const isSuccess = params.status !== "error";
  const isExpoGo = isExpoGoRuntime();

  useEffect(() => {
    // Animate success indicator
    Animated.sequence([
      Animated.parallel([
        Animated.spring(scaleAnim, {
          toValue: 1,
          useNativeDriver: true,
        }),
        Animated.timing(opacityAnim, {
          toValue: 1,
          duration: 300,
          useNativeDriver: true,
        }),
      ]),
    ]).start();
  }, [scaleAnim, opacityAnim]);

  const trip = {
    date: "May 18, 2024",
    time: "2:45 PM",
    route: "101 Downtown Express",
    from: "Central Station",
    to: "Airport Terminal",
    stops: 12,
    fare: "$2.75",
    balanceAfter: "$42.75",
    ticketId: "TKT-2024-18-001",
  };

  return (
    <ScrollView
      style={{ flex: 1, backgroundColor: theme.colors.background }}
      contentContainerStyle={{ flexGrow: 1 }}
    >
      {/* Success Animation */}
      <View
        style={{
          alignItems: "center",
          justifyContent: "center",
          paddingVertical: 40,
          paddingTop: 60,
        }}
      >
        <Animated.View
          style={{
            transform: [{ scale: scaleAnim }],
            opacity: opacityAnim,
          }}
        >
          <View
            style={{
              width: 120,
              height: 120,
              borderRadius: 60,
              backgroundColor: isSuccess ? "#4CAF50" : "#D32F2F",
              justifyContent: "center",
              alignItems: "center",
            }}
          >
            <Text
              style={{
                fontSize: 60,
                color: "#fff",
              }}
            >
              {isSuccess ? "✓" : "!"}
            </Text>
          </View>
        </Animated.View>

        <Text
          variant="displayMedium"
          style={{
            fontWeight: "bold",
            marginTop: 24,
            color: isSuccess ? "#4CAF50" : "#D32F2F",
          }}
        >
          {isSuccess ? "Tap Successful!" : "Tap Failed"}
        </Text>
        <Text
          variant="bodyLarge"
          style={{
            color: theme.colors.onSurfaceVariant,
            marginTop: 8,
            textAlign: "center",
          }}
        >
          {isSuccess
            ? "Your ticket has been validated"
            : params.reason === "missing-token"
            ? "No NFC token was found in secure storage"
            : "HCE could not complete this tap"}
        </Text>
      </View>

      {isExpoGo && (
        <Card
          style={{
            marginHorizontal: 16,
            marginBottom: 16,
            backgroundColor: "#FFF4E5",
            borderLeftWidth: 4,
            borderLeftColor: "#FF9800",
          }}
        >
          <Card.Content>
            <Text variant="bodyMedium" style={{ color: "#8D5D00" }}>
              HCE is disabled in Expo Go. Use your Android development or production build to test tap emulation.
            </Text>
          </Card.Content>
        </Card>
      )}

      {/* Trip Details */}
      <Card
        style={{
          marginHorizontal: 16,
          marginBottom: 16,
          backgroundColor: theme.colors.surface,
        }}
      >
        <Card.Title title="Trip Details" titleVariant="titleMedium" />
        <Divider />
        <Card.Content style={{ paddingVertical: 12 }}>
          <List.Item
            title="Route"
            description={trip.route}
            left={(props) => <List.Icon {...props} icon="bus" />}
            descriptionNumberOfLines={2}
          />
          <List.Item
            title="From"
            description={trip.from}
            left={(props) => <List.Icon {...props} icon="map-marker" />}
          />
          <List.Item
            title="To"
            description={trip.to}
            left={(props) => <List.Icon {...props} icon="map-marker-check" />}
          />
          <List.Item
            title="Stops"
            description={`${trip.stops} stops`}
            left={(props) => <List.Icon {...props} icon="sign-multiple" />}
          />
        </Card.Content>
      </Card>

      {/* Transaction Details */}
      <Card
        style={{
          marginHorizontal: 16,
          marginBottom: 16,
          backgroundColor: theme.colors.surface,
        }}
      >
        <Card.Title title="Transaction" titleVariant="titleMedium" />
        <Divider />
        <Card.Content>
          <View
            style={{
              flexDirection: "row",
              justifyContent: "space-between",
              marginBottom: 12,
            }}
          >
            <Text variant="bodyMedium" style={{ color: theme.colors.onSurfaceVariant }}>
              Fare Charged
            </Text>
            <Text variant="bodyMedium" style={{ fontWeight: "bold" }}>
              {trip.fare}
            </Text>
          </View>
          <Divider style={{ marginVertical: 8 }} />
          <View
            style={{
              flexDirection: "row",
              justifyContent: "space-between",
            }}
          >
            <Text variant="bodyMedium" style={{ color: theme.colors.onSurfaceVariant }}>
              Balance After
            </Text>
            <Text
              variant="titleMedium"
              style={{ fontWeight: "bold", color: theme.colors.primary }}
            >
              {trip.balanceAfter}
            </Text>
          </View>
        </Card.Content>
      </Card>

      {/* Time and ID */}
      <Card
        style={{
          marginHorizontal: 16,
          marginBottom: 16,
          backgroundColor: theme.colors.surfaceVariant,
        }}
      >
        <Card.Content>
          <View
            style={{
              flexDirection: "row",
              justifyContent: "space-between",
              alignItems: "center",
              gap: 16,
            }}
          >
            <View style={{ flex: 1 }}>
              <Text
                variant="bodySmall"
                style={{
                  color: theme.colors.onSurfaceVariant,
                  marginBottom: 4,
                }}
              >
                Scanned Time
              </Text>
              <Text variant="titleMedium" style={{ fontWeight: "bold" }}>
                {trip.time}
              </Text>
            </View>
            <Divider />
            <View style={{ flex: 1 }}>
              <Text
                variant="bodySmall"
                style={{
                  color: theme.colors.onSurfaceVariant,
                  marginBottom: 4,
                }}
              >
                Ticket ID
              </Text>
              <Text
                variant="titleSmall"
                style={{ fontWeight: "bold", textAlign: "right" }}
              >
                {trip.ticketId}
              </Text>
            </View>
          </View>
        </Card.Content>
      </Card>

      {/* Info Message */}
      <Card
        style={{
          marginHorizontal: 16,
          marginBottom: 24,
          backgroundColor: "#E8F5E9",
          borderLeftWidth: 4,
          borderLeftColor: "#4CAF50",
        }}
      >
        <Card.Content>
          <Text
            variant="bodyMedium"
            style={{ color: "#2E7D32", textAlign: "center" }}
          >
            You are all set! Enjoy your trip. Your boarding pass is saved in your account.
          </Text>
        </Card.Content>
      </Card>

      {/* Action Buttons */}
      <View style={{ paddingHorizontal: 16, marginBottom: 24, gap: 12 }}>
        <Button
          mode="contained"
          onPress={() => router.back()}
          style={{ paddingVertical: 8 }}
        >
          Continue
        </Button>
        <Button
          mode="outlined"
          onPress={() => console.log("View receipt")}
          style={{ paddingVertical: 8 }}
        >
          View Receipt
        </Button>
      </View>
    </ScrollView>
  );
}