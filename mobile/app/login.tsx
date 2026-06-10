import { useState } from "react";
import { ScrollView, View } from "react-native";
import { Appbar, Button, TextInput, Text, useTheme } from "react-native-paper";
import { useRouter } from "expo-router";
import { login } from "@/helpers/login";

export default function Login() {
    const theme = useTheme();
    const router = useRouter();

    const [loading, setLoading] = useState(false);
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [hidePassword, setHidePassword] = useState(true);

    const handleLogin = async () => {
        setLoading(true);

        try {
            await login({ email, password });

            router.replace("/");
        } catch (error) {
            console.error("Login failed:", error);
            alert(error instanceof Error ? error.message : "An unknown error occurred");
        } finally {
            setLoading(false);
        }
    };

    return (
        <>
            <Appbar.Header>
                <Appbar.BackAction onPress={() => router.back()} />
                <Appbar.Content title="Login" />
            </Appbar.Header>

            <ScrollView
                style={{
                    flex: 1,
                    padding: 24,
                    backgroundColor: theme.colors.background,
                }}
                contentContainerStyle={{ justifyContent: "center", minHeight: "100%" }}
            >
                <View style={{ marginBottom: 32 }}>
                    <Text variant="displaySmall" style={{ marginBottom: 8, fontWeight: "bold" }}>
                        Welcome Back
                    </Text>
                    <Text variant="bodyMedium" style={{ color: theme.colors.onSurfaceVariant }}>
                        Sign in to your account to continue
                    </Text>
                </View>

                <TextInput
                    label="Email"
                    value={email}
                    onChangeText={setEmail}
                    mode="outlined"
                    keyboardType="email-address"
                    placeholder="Enter your email"
                    style={{ marginBottom: 16 }}
                    disabled={loading}
                />

                <TextInput
                    label="Password"
                    value={password}
                    onChangeText={setPassword}
                    mode="outlined"
                    placeholder="Enter your password"
                    secureTextEntry={hidePassword}
                    right={
                        <TextInput.Icon
                            icon={hidePassword ? "eye-off" : "eye"}
                            onPress={() => setHidePassword(!hidePassword)}
                        />
                    }
                    style={{ marginBottom: 24 }}
                    disabled={loading}
                />

                <Button
                    mode="contained"
                    onPress={handleLogin}
                    style={{ marginBottom: 16 }}
                    loading={loading}
                >
                    Sign In
                </Button>

                <View style={{ flexDirection: "row", justifyContent: "center", marginBottom: 24 }}>
                    <Text variant="bodyMedium">Don&apos;t have an account? </Text>
                    <Button
                        mode="text"
                        onPress={() => router.push("/signup")}
                        style={{ marginLeft: -8 }}
                        disabled={loading}
                    >
                        Sign Up
                    </Button>
                </View>

                <Button
                    mode="text"
                    onPress={() => console.log("Forgot password")}
                    disabled={loading}
                >
                    Forgot Password?
                </Button>
            </ScrollView>
        </>
    );
}
