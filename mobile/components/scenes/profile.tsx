import { ScrollView, View } from "react-native";
import {
    Appbar,
    Avatar,
    Button,
    Card,
    Divider,
    List,
    MD3Theme,
    Text,
    useTheme,
} from "react-native-paper";
import { Router, useRouter } from "expo-router";
import { useCustomer } from "@/helpers/customer";
import { Customer } from "@/types";

interface LoggedInProfileProps {
    theme: MD3Theme;
    router: Router;
    customer: Customer;
}

function LoggedInProfile({theme, router, customer}: LoggedInProfileProps) {

    return <>
        <Appbar.Header>
            <Appbar.Content title="My Profile" />
        </Appbar.Header>
        <ScrollView style={{ flex: 1, backgroundColor: theme.colors.background }}>

            {/* Profile Header */}
            <Card
                style={{
                    margin: 16,
                    backgroundColor: theme.colors.surface,
                }}
            >
                <Card.Content style={{ paddingVertical: 20 }}>
                    <View style={{ alignItems: "center" }}>
                        <Avatar.Image size={80} source={{ uri: "https://via.placeholder.com/80" }} />
                        <Text variant="titleLarge" style={{ marginTop: 12, fontWeight: "bold" }}>
                            {customer.first_name} {customer.last_name}
                        </Text>
                        {/* <Text
                            variant="bodyMedium"
                            style={{ color: theme.colors.onSurfaceVariant, marginTop: 4 }}
                        >
                            {userProfile.membershipTier} Member
                        </Text> */}
                    </View>
                </Card.Content>
            </Card>

            {/* Card Balance */}
            <Card
                style={{
                    marginHorizontal: 16,
                    marginBottom: 16,
                    backgroundColor: theme.colors.primary,
                }}
            >
                <Card.Content>
                    <Text
                        variant="bodyMedium"
                        style={{
                            color: theme.colors.onPrimary,
                            marginBottom: 8,
                            opacity: 0.9,
                        }}
                    >
                        Transit Card Balance
                    </Text>
                    <Text
                        variant="displaySmall"
                        style={{
                            color: theme.colors.onPrimary,
                            fontWeight: "bold",
                        }}
                    >
                        {/* ${userProfile.cardBalance.toFixed(2)} */}
                        0
                    </Text>
                </Card.Content>
                <Card.Actions>
                    <Button textColor={theme.colors.onPrimary}>Add Funds</Button>
                </Card.Actions>
            </Card>

            {/* Account Details */}
            <Card style={{ marginHorizontal: 16, marginBottom: 16 }}>
                <Card.Title title="Account Details" titleVariant="titleMedium" />
                <Divider />
                <Card.Content>
                    <List.Item
                        title="Email"
                        description={customer.email}
                        left={(props) => <List.Icon {...props} icon="email" />}
                    />
                    <List.Item
                        title="Phone"
                        description={customer.phone}
                        left={(props) => <List.Icon {...props} icon="phone" />}
                    />
                    <List.Item
                        title="Member Since"
                        description={customer.registered_date ? new Date(customer.registered_date).toLocaleDateString() : "N/A"}
                        left={(props) => <List.Icon {...props} icon="calendar" />}
                    />
                </Card.Content>
            </Card>

            {/* Transit Benefits */}
            <Card style={{ marginHorizontal: 16, marginBottom: 16 }}>
                <Card.Title title="Transit Benefits" titleVariant="titleMedium" />
                <Divider />
                <Card.Content>
                    <List.Item
                        title="Unlimited Routes"
                        description="Access to all transit routes"
                        left={(props) => <List.Icon {...props} icon="check-circle" />}
                    />
                    <List.Item
                        title="Priority Support"
                        description="24/7 customer support"
                        left={(props) => <List.Icon {...props} icon="check-circle" />}
                    />
                    <List.Item
                        title="Discount Passes"
                        description="Exclusive discounts on monthly passes"
                        left={(props) => <List.Icon {...props} icon="check-circle" />}
                    />
                </Card.Content>
            </Card>

            {/* Actions */}
            <Card style={{ marginHorizontal: 16, marginBottom: 24 }}>
                <Card.Content>
                    <Button
                        mode="outlined"
                        onPress={() => console.log("Edit profile")}
                        style={{ marginBottom: 12 }}
                    >
                        Edit Profile
                    </Button>
                    <Button
                        mode="outlined"
                        onPress={() => console.log("Payment methods")}
                        style={{ marginBottom: 12 }}
                    >
                        Payment Methods
                    </Button>
                    <Button
                        mode="outlined"
                        onPress={() => console.log("Settings")}
                        style={{ marginBottom: 12 }}
                    >
                        Settings
                    </Button>
                    <Button
                        mode="outlined"
                        textColor="#d32f2f"
                        onPress={() => {
                            console.log("Logged out");
                        }}
                    >
                        Sign Out
                    </Button>
                </Card.Content>
            </Card>
        </ScrollView>
    </>;
}

interface LoggedOutProfileProps {
    theme: MD3Theme;
    router: Router;
}

function LoggedOutProfile({theme, router}: LoggedOutProfileProps) {

    return <ScrollView
        style={{
            flex: 1,
            backgroundColor: theme.colors.background,
            padding: 16,
        }}
        contentContainerStyle={{ justifyContent: "center", minHeight: "100%" }}
    >
        <View style={{ alignItems: "center", marginBottom: 32 }}>
            <Avatar.Icon
                size={80}
                icon="account-off"
                style={{ backgroundColor: theme.colors.primary }}
            />
            <Text
                variant="displaySmall"
                style={{ marginTop: 16, marginBottom: 8, fontWeight: "bold" }}
            >
                Not Logged In
            </Text>
            <Text
                variant="bodyMedium"
                style={{ color: theme.colors.onSurfaceVariant, textAlign: "center" }}
            >
                Sign in to view your transit account and access all features
            </Text>
        </View>

        <Button
            mode="contained"
            onPress={() => router.push("/login")}
            style={{ marginBottom: 12 }}
        >
            Sign In
        </Button>

        <Button mode="outlined" onPress={() => router.push("/signup")}>
            Create Account
        </Button>
    </ScrollView>;
}

export default function ProfileScene() {
    const theme = useTheme();
    const router = useRouter();

    const { customer, loading } = useCustomer();
    
    if (loading) {
        return <View style={{ flex: 1, justifyContent: "center", alignItems: "center" }}>
            <Text>Loading...</Text>
        </View>;
    }

    const isLoggedIn = !!customer?.id;

    if (!isLoggedIn) {
        return <LoggedOutProfile theme={theme} router={router} />;
    }

    return <LoggedInProfile theme={theme} router={router} customer={customer} />;
}