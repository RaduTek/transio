import { useState } from "react";
import { KeyboardAvoidingView, ScrollView, View } from "react-native";
import { Appbar, Button, TextInput, Text, useTheme } from "react-native-paper";
import { useRouter } from "expo-router";
import { signup } from "@/helpers/login";

export default function SignUp() {
    const theme = useTheme();
    const router = useRouter();
    const [loading, setLoading] = useState(false);
    const [name, setName] = useState("");
    const [phone, setPhone] = useState("");
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [confirmPassword, setConfirmPassword] = useState("");
    const [hidePassword, setHidePassword] = useState(true);
    const [hideConfirmPassword, setHideConfirmPassword] = useState(true);

    const handleSignUp = async () => {
        if (password !== confirmPassword) {
            alert("Passwords do not match!");
            return;
        }

        const trimmedName = name.trim();
        const [first_name, ...rest] = trimmedName.split(/\s+/);
        const last_name = rest.join(" ");

        if (!first_name) {
            alert("Please enter your full name");
            return;
        }

        if (!phone.trim()) {
            alert("Please enter your phone number");
            return;
        }

        setLoading(true);

        try {
            await signup({
                email: email.trim(),
                phone: phone.trim(),
                first_name,
                last_name,
                password,
            });

            router.replace("/");
        } catch (error) {
            console.error("Signup failed:", error);
            alert(error instanceof Error ? error.message : "An unknown error occurred");
        } finally {
            setLoading(false);
        }
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
                        disabled={loading}
                    />

                    <TextInput
                        label="Phone"
                        value={phone}
                        onChangeText={setPhone}
                        mode="outlined"
                        keyboardType="phone-pad"
                        placeholder="Enter your phone number"
                        style={{ marginBottom: 16 }}
                        disabled={loading}
                    />

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
                        placeholder="Create a password"
                        secureTextEntry={hidePassword}
                        right={
                            <TextInput.Icon
                                icon={hidePassword ? "eye-off" : "eye"}
                                onPress={() => setHidePassword(!hidePassword)}
                            />
                        }
                        style={{ marginBottom: 16 }}
                        disabled={loading}
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
                        disabled={loading}
                    />

                    <Button
                        mode="contained"
                        onPress={handleSignUp}
                        style={{ marginBottom: 16 }}
                        loading={loading}
                        disabled={loading}
                    >
                        Create Account
                    </Button>

                    <View style={{ flexDirection: "row", justifyContent: "center" }}>
                        <Text variant="bodyMedium">Already have an account? </Text>
                        <Button
                            mode="text"
                            onPress={() => router.push("/login")}
                            style={{ marginLeft: -8 }}
                            disabled={loading}
                        >
                            Sign In
                        </Button>
                    </View>
                </ScrollView>

            </KeyboardAvoidingView>
        </>
    );
}
