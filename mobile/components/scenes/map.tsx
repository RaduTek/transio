import { StyleSheet, View, Text, ActivityIndicator } from 'react-native';
import MapView, { Marker, PROVIDER_GOOGLE } from 'react-native-maps';
import { useQuery } from '@tanstack/react-query';
import { fetchApi } from '@/helpers/net';
import { TransitStop } from "@/types/transit";

const INITIAL_REGION = {
    latitude: 40.7128,
    longitude: -74.0060,
    latitudeDelta: 0.1,
    longitudeDelta: 0.1,
};

const styles = StyleSheet.create({
    container: {
        flex: 1,
        justifyContent: 'center',
        alignItems: 'center',
    },
    map: {
        flex: 1,
        width: '100%',
    },
    errorText: {
        fontSize: 16,
        color: 'red',
        textAlign: 'center',
        paddingHorizontal: 20,
    },
});

const STOPS_QUERY_KEY = ['stops'];

async function fetchStops(): Promise<TransitStop[]> {
    const response = await fetchApi('/public/stops');
    
    if (!response.ok) {
        throw new Error(`Failed to fetch stops: ${response.statusText}`);
    }
    
    return response.json();
}

export default function MapScene() {
    const { data: stops = [], isLoading, error } = useQuery({
        queryKey: STOPS_QUERY_KEY,
        queryFn: fetchStops,
    });

    if (isLoading) {
        return (
            <View style={styles.container}>
                <ActivityIndicator size="large" color="#0000ff" />
            </View>
        );
    }

    if (error) {
        return (
            <View style={styles.container}>
                <Text style={styles.errorText}>
                    Error: {error instanceof Error ? error.message : 'Unknown error occurred'}
                </Text>
            </View>
        );
    }

    return (
        <View style={styles.container}>
            <MapView
                style={styles.map}
                initialRegion={INITIAL_REGION}
                provider={PROVIDER_GOOGLE}
            >
                {stops.map((stop) => (
                    <Marker
                        key={stop.id}
                        coordinate={{
                            latitude: stop.lat,
                            longitude: stop.lon,
                        }}
                        title={stop.name}
                        description={stop.description || stop.address}
                    />
                ))}
            </MapView>
        </View>
    );
}
