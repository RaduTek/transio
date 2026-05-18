import {
  MD3LightTheme as LightTheme,
  MD3DarkTheme as DarkTheme,
  PaperProvider
} from 'react-native-paper';
import { useColorScheme } from 'react-native';
import {
  ThemeProvider as NavThemeProvider,
  DefaultTheme as NavLightTheme,
  DarkTheme as NavDarkTheme
} from '@react-navigation/native';
import { Stack } from "expo-router";

const lightTheme = {
  ...LightTheme,
  colors: {
    ...LightTheme.colors,
    primary: '#6200ee',
    accent: '#03dac4',
    background: '#f6f6f6',
    surface: '#ffffff',
    text: '#000000',
    disabled: 'rgba(0, 0, 0, 0.26)',
    placeholder: 'rgba(0, 0, 0, 0.54)',
    backdrop: 'rgba(0, 0, 0, 0.5)',
  },
};

const darkTheme = {
  ...DarkTheme,
  colors: {
    ...DarkTheme.colors,
    primary: '#bb86fc',
    accent: '#03dac6',
    background: '#121212',
    surface: '#1e1e1e',
    text: '#ffffff',
    disabled: 'rgba(255, 255, 255, 0.38)',
    placeholder: 'rgba(255, 255, 255, 0.60)',
    backdrop: 'rgba(0, 0, 0, 0.7)',
  },
};

export default function RootLayout() {
  const colorScheme = useColorScheme();
  const paperTheme = colorScheme === 'dark' ? darkTheme : lightTheme;
  const navTheme = colorScheme === 'dark' ? NavDarkTheme : NavLightTheme;

  return <PaperProvider theme={paperTheme}>
    <NavThemeProvider value={navTheme}>
      <Stack screenOptions={{
        headerShown: false,
        contentStyle: { backgroundColor: paperTheme.colors.background },
      }} />
    </NavThemeProvider>
  </PaperProvider>;
}
