import React from 'react';
import { StyleSheet, View, ActivityIndicator, Text } from 'react-native';
import { Redirect } from 'expo-router';
import { useAuth } from '../contexts/AuthContext';

export default function IndexScreen() {
    const { isAuthenticated, isLoading } = useAuth();

    //   if (isLoading) {
    //     return (
    //       <View style={styles.loadingContainer}>
    //         <ActivityIndicator size="large" color="#0a7ea4" />
    //         <Text style={styles.loadingText}>Loading...</Text>
    //       </View>
    //     );
    //   }

    //   if (isAuthenticated) {
    //     return <Redirect href="/(tabs)" />;
    //   } else {
    //     return <Redirect href="/auth/login" />;
    //   }
    return <Redirect href="/(tabs)" />;
}

const styles = StyleSheet.create({
    loadingContainer: {
        flex: 1,
        justifyContent: 'center',
        alignItems: 'center',
        gap: 16,
    },
    loadingText: {
        fontSize: 16,
    },
});
