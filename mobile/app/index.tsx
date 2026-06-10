import { useState } from "react";
import { BottomNavigation } from "react-native-paper";
import RoutesScene from "@/components/scenes/routes";
import MapScene from "@/components/scenes/map";
import SearchScene from "@/components/scenes/search";
import ProfileScene from "@/components/scenes/profile";

const routes = [
  { key: 'routes', title: 'Routes', focusedIcon: 'routes' },
  { key: 'map', title: 'Map', focusedIcon: 'map' },
  // { key: 'search', title: 'Search', focusedIcon: 'magnify' },
  { key: 'profile', title: 'Profile', focusedIcon: 'account', unfocusedIcon: 'account-outline' },
];

export default function MainLayout() {
    const [index, setIndex] = useState(0);

    const renderScene = BottomNavigation.SceneMap({
      routes: RoutesScene,
      map: MapScene,
      search: SearchScene,
      profile: ProfileScene,
    });

    return <BottomNavigation
      navigationState={{ index, routes }}
      onIndexChange={setIndex}
      renderScene={renderScene}
    />;
}