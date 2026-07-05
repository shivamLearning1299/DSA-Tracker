import { GoogleLogin } from "@react-oauth/google";
import { useNavigate } from "react-router-dom";

import { useAuth } from "./AuthContext";

export function GoogleLoginButton() {
  const { loginWithGoogle } = useAuth();
  const navigate = useNavigate();

  return (
    <GoogleLogin
      useOneTap
      onSuccess={async (response) => {
        if (!response.credential) return;
        await loginWithGoogle(response.credential);
        navigate("/dashboard");
      }}
      onError={() => {
        console.error("Google sign-in failed");
      }}
    />
  );
}
