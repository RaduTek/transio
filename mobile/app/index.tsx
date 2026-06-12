import { useState } from "react";
import { BottomNavigation } from "react-native-paper";
import RoutesScene from "@/components/scenes/routes";
import PlanJourneyScene from "@/components/scenes/planjourney";
import SearchScene from "@/components/scenes/search";
import ProfileScene from "@/components/scenes/profile";

const routes = [
  { key: 'routes', title: 'Routes', focusedIcon: 'routes' },
  { key: 'plan', title: 'Plan', focusedIcon: 'map-marker-path' },
  // { key: 'search', title: 'Search', focusedIcon: 'magnify' },
  { key: 'profile', title: 'Profile', focusedIcon: 'account', unfocusedIcon: 'account-outline' },
];

export default function MainLayout() {
    const [index, setIndex] = useState(0);

    const renderScene = BottomNavigation.SceneMap({
      routes: RoutesScene,
      plan: PlanJourneyScene,
      search: SearchScene,
      profile: ProfileScene,
    });

    return <BottomNavigation
      navigationState={{ index, routes }}
      onIndexChange={setIndex}
      renderScene={renderScene}
    />;
}