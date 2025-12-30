"use client";

import { RegisterForm } from "@/components/auth/RegisterForm";
import { Suspense } from "react";

export default function RegisterPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 p-4">
      <Suspense fallback={
        <div className="w-full max-w-md">
          <div className="h-64 bg-white rounded-lg shadow animate-pulse" />
        </div>
      }>
        <RegisterForm />
      </Suspense>
    </div>
  );
}


