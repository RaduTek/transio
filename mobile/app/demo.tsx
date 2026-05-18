import { useState } from "react";
import { KeyboardAvoidingView, ScrollView, View } from "react-native";
import {
  Appbar,
  Button,
  Card,
  Chip,
  FAB,
  TextInput,
  Text,
  useTheme,
} from "react-native-paper";
import { useRouter } from "expo-router";

export default function Index() {
  const theme = useTheme();
  const router = useRouter();
  const [text, setText] = useState("");
  const [selectedChip, setSelectedChip] = useState<string | null>(null);

  return (
    <KeyboardAvoidingView style={{ flex: 1 }} behavior="padding">
      <Appbar.Header>
        <Appbar.Content title="React Native Paper Demo" />
      </Appbar.Header>

      <ScrollView style={{ flex: 1, padding: 16, backgroundColor: theme.colors.background }}>
        {/* Navigation Section */}
        <View style={{ flexDirection: "row", gap: 8, marginBottom: 24 }}>
          <Button
            mode="outlined"
            onPress={() => router.push("/login")}
            style={{ flex: 1 }}
          >
            Login
          </Button>
          <Button
            mode="outlined"
            onPress={() => router.push("/signup")}
            style={{ flex: 1 }}
          >
            Sign Up
          </Button>
        </View>

        {/* Title Section */}
        <Text variant="titleLarge" style={{ marginBottom: 16 }}>Welcome to Paper UI</Text>
        <Text variant="bodyMedium">
          This is a simple demo showcasing various React Native Paper components
          with full dark mode support synced to your system settings.
        </Text>

        {/* Card Section */}
        <Card style={{ marginVertical: 16 }}>
          <Card.Cover source={require("../assets/images/partial-react-logo.png")} />
          <Card.Content>
            <Text variant="titleMedium" style={{ marginTop: 10 }}>Card Component</Text>
            <Text variant="bodyMedium">
              Cards are used to display related grouping of information.
            </Text>
          </Card.Content>
          <Card.Actions>
            <Button>Cancel</Button>
            <Button mode="contained">Save</Button>
          </Card.Actions>
        </Card>

        {/* Buttons Section */}
        <Text variant="titleMedium" style={{ marginTop: 20, marginBottom: 10 }}>
          Buttons
        </Text>
        <Button mode="contained" onPress={() => {}}>
          Contained Button
        </Button>
        <Button
          mode="outlined"
          onPress={() => {}}
          style={{ marginTop: 10 }}
        >
          Outlined Button
        </Button>
        <Button
          mode="text"
          onPress={() => {}}
          style={{ marginTop: 10 }}
        >
          Text Button
        </Button>

        {/* TextInput Section */}
        <Text variant="titleMedium" style={{ marginTop: 20, marginBottom: 10 }}>Input</Text>
        <TextInput
          label="Enter text"
          value={text}
          onChangeText={setText}
          mode="outlined"
          placeholder="Type something..."
        />

        {/* Chips Section */}
        <Text variant="titleMedium" style={{ marginTop: 20, marginBottom: 10 }}>
          Chips
        </Text>
        <ScrollView horizontal showsHorizontalScrollIndicator={false}>
          {["React", "Native", "Paper", "UI"].map((chip) => (
            <Chip
              key={chip}
              selected={selectedChip === chip}
              onPress={() => setSelectedChip(chip)}
              style={{ marginRight: 8 }}
            >
              {chip}
            </Chip>
          ))}
        </ScrollView>

        {/* Info Card */}
        <Card style={{ marginVertical: 20, marginBottom: 80 }}>
          <Card.Content>
            <Text variant="titleMedium">Selected: {selectedChip || "None"}</Text>
            <Text variant="bodyMedium">Input value: {text || "Empty"}</Text>
          </Card.Content>
        </Card>
      </ScrollView>

      <FAB
        icon="plus"
        onPress={() => {}}
        style={{ position: "absolute", margin: 16, right: 0, bottom: 0 }}
      />
    </KeyboardAvoidingView>
  );
}
