import { useState } from "react";
import { KeyboardAvoidingView, ScrollView, View } from "react-native";
import { Appbar, Button, TextInput, Text, useTheme } from "react-native-paper";
import { useRouter } from "expo-router";

export default function SignUp() {
    const theme = useTheme();
    const router = useRouter();
    const [name, setName] = useState("");
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [confirmPassword, setConfirmPassword] = useState("");
    const [hidePassword, setHidePassword] = useState(true);
    const [hideConfirmPassword, setHideConfirmPassword] = useState(true);

    const handleSignUp = () => {
        // Handle sign-up logic here
        if (password !== confirmPassword) {
            alert("Passwords do not match!");
            return;
        }
        console.log("Sign up with:", name, email, password);
        // Navigate to home after signup
        router.replace("/");
    };

    return (
        <>
            <Appbar.Header>
                <Appbar.BackAction onPress={() => router.back()} />
                <Appbar.Content title="Create Account" />
            </Appbar.Header>

            <KeyboardAvoidingView style={{ flex: 1 }} behavior="padding">
            <ScrollView
                style={{
                    flex: 1,
                    padding: 24,
                    backgroundColor: theme.colors.background,
                }}
                contentContainerStyle={{ paddingVertical: 24 }}
            >
                <View style={{ marginBottom: 24 }}>
                    <Text variant="displaySmall" style={{ marginBottom: 8, fontWeight: "bold" }}>
                        Join Us
                    </Text>
                    <Text variant="bodyMedium" style={{ color: theme.colors.onSurfaceVariant }}>
                        Create a new account to get started
                    </Text>
                </View>

                <TextInput
                    label="Full Name"
                    value={name}
                    onChangeText={setName}
                    mode="outlined"
                    placeholder="Enter your full name"
                    style={{ marginBottom: 16 }}
                />

                <TextInput
                    label="Email"
                    value={email}
                    onChangeText={setEmail}
                    mode="outlined"
                    keyboardType="email-address"
                    placeholder="Enter your email"
                    style={{ marginBottom: 16 }}
                />

                <TextInput
                    label="Password"
                    value={password}
                    onChangeText={setPassword}
                    mode="outlined"
                    placeholder="Create a password"
                    secureTextEntry={hidePassword}
                    right={
                        <TextInput.Icon
                            icon={hidePassword ? "eye-off" : "eye"}
                            onPress={() => setHidePassword(!hidePassword)}
                        />
                    }
                    style={{ marginBottom: 16 }}
                />

                <TextInput
                    label="Confirm Password"
                    value={confirmPassword}
                    onChangeText={setConfirmPassword}
                    mode="outlined"
                    placeholder="Confirm your password"
                    secureTextEntry={hideConfirmPassword}
                    right={
                        <TextInput.Icon
                            icon={hideConfirmPassword ? "eye-off" : "eye"}
                            onPress={() => setHideConfirmPassword(!hideConfirmPassword)}
                        />
                    }
                    style={{ marginBottom: 24 }}
                />

                <Button
                    mode="contained"
                    onPress={handleSignUp}
                    style={{ marginBottom: 16 }}
                >
                    Create Account
                </Button>

                <View style={{ flexDirection: "row", justifyContent: "center" }}>
                    <Text variant="bodyMedium">Already have an account? </Text>
                    <Button
                        mode="text"
                        onPress={() => router.push("/login")}
                        style={{ marginLeft: -8 }}
                    >
                        Sign In
                    </Button>
                </View>
            </ScrollView>

            </KeyboardAvoidingView>
        </>
    );
}
