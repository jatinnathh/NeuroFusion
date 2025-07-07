import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  ActivityIndicator,
  StyleSheet,
  TouchableOpacity,
  Alert,
  Platform,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useNavigation } from '@react-navigation/native';
import ipConfig from './ip.json';

export default function Account({ route }) {
  const userId = route?.params?.userId;
  const [isLoggingOut, setIsLoggingOut] = useState(false);
  const [hasLoggedOut, setHasLoggedOut] = useState(false);
  const [userInfo, setUserInfo] = useState(null);
  const navigation = useNavigation();
  const backendURL = `http://${ipConfig.ip}:8000`;

  useEffect(() => {
    if (hasLoggedOut && !isLoggingOut) {
      navigation.reset({
        index: 0,
        routes: [{ name: 'Login' }],
      });
    }
  }, [hasLoggedOut, isLoggingOut, navigation]);

  useEffect(() => {
    if (!userId || isLoggingOut || hasLoggedOut) return;

    const fetchUserInfo = async () => {
      try {
        const res = await fetch(`${backendURL}/user-info/${userId}`);
        const data = await res.json();
        setUserInfo(data);
      } catch (err) {
        console.error("Failed to fetch user info", err);
      }
    };

    fetchUserInfo();
  }, [userId, isLoggingOut, hasLoggedOut]);

  const handleLogout = async () => {
    try {
      setIsLoggingOut(true);
      await fetch(`${backendURL}/logout/${userId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
      });

      setUserInfo(null);
      navigation.reset({ index: 0, routes: [{ name: 'Login' }] });
    } catch (err) {
      console.error("Logout error:", err);
      setUserInfo(null);
      navigation.reset({ index: 0, routes: [{ name: 'Login' }] });
    } finally {
      setIsLoggingOut(false);
      setHasLoggedOut(true);
    }
  };

  if (!userInfo && !isLoggingOut && !hasLoggedOut) {
    return (
      <LinearGradient colors={['#1a1a1a', '#000']} style={styles.container}>
        <SafeAreaView style={styles.centered}>
          <ActivityIndicator size="large" color="#fff" />
          <Text style={styles.loadingText}>Loading account info...</Text>
        </SafeAreaView>
      </LinearGradient>
    );
  }

  if (isLoggingOut) {
    return (
      <LinearGradient colors={['#1a1a1a', '#000']} style={styles.container}>
        <SafeAreaView style={styles.centered}>
          <ActivityIndicator size="large" color="#fff" />
          <Text style={styles.loadingText}>Logging out...</Text>
        </SafeAreaView>
      </LinearGradient>
    );
  }

  if (!userInfo && !hasLoggedOut) {
    return (
      <LinearGradient colors={['#1a1a1a', '#000']} style={styles.container}>
        <SafeAreaView style={styles.centered}>
          <Text style={styles.errorText}>Failed to load account information</Text>
          <TouchableOpacity
            style={styles.button}
            onPress={() => navigation.reset({ index: 0, routes: [{ name: 'Login' }] })}
          >
            <Text style={styles.buttonText}>Back to Login</Text>
          </TouchableOpacity>
        </SafeAreaView>
      </LinearGradient>
    );
  }

  return (
    <LinearGradient colors={['#1a1a1a', '#000']} style={styles.container}>
      <SafeAreaView style={styles.inner}>
        <Text style={styles.title}>Welcome, {userInfo.username}</Text>

        <View style={styles.section}>
          <Text style={styles.label}>Email</Text>
          <Text style={styles.value}>{userInfo.email}</Text>
        </View>

        <View style={styles.section}>
          <Text style={styles.label}>Joined</Text>
          <Text style={styles.value}>{userInfo.created_at?.split('T')[0]}</Text>
        </View>

        <View style={styles.section}>
          <Text style={styles.label}>Total Generations</Text>
          <Text style={styles.value}>{userInfo.total_images}</Text>
        </View>

        <TouchableOpacity style={styles.logoutBtn} onPress={handleLogout}>
          <Text style={styles.logoutText}>Logout</Text>
        </TouchableOpacity>
      </SafeAreaView>
    </LinearGradient>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  centered: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    color: '#fff',
    marginTop: 10,
    fontSize: 16,
  },
  errorText: {
    color: '#ff4444',
    fontSize: 16,
    marginBottom: 20,
    textAlign: 'center',
  },
  button: {
    backgroundColor: '#007AFF',
    paddingVertical: 12,
    paddingHorizontal: 20,
    borderRadius: 8,
    alignItems: 'center',
  },
  buttonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  inner: {
    flex: 1,
    paddingHorizontal: 24,
    paddingTop: 50,
    paddingBottom: 30,
    maxWidth: 600,
    alignSelf: 'center',
    width: '100%',
  },
  title: {
    color: '#fff',
    fontSize: 26,
    fontWeight: 'bold',
    marginBottom: 28,
    textAlign: 'center',
  },
  section: {
    backgroundColor: '#111',
    padding: 18,
    borderRadius: 12,
    marginBottom: 14,
    borderWidth: 1,
    borderColor: '#222',
  },
  label: {
    color: '#888',
    fontSize: 13,
    marginBottom: 4,
  },
  value: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '500',
  },
  logoutBtn: {
    marginTop: 32,
    backgroundColor: '#ff4444',
    paddingVertical: 14,
    borderRadius: 12,
    alignItems: 'center',
    ...(Platform.OS === 'web' && {
      cursor: 'pointer',
      transition: 'background-color 0.3s',
    }),
  },
  logoutText: {
    color: '#fff',
    fontWeight: 'bold',
    fontSize: 16,
  },
});
