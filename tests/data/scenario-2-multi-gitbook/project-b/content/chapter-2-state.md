# Kapitel 2: State Management

## 2.1 Redux Toolkit

Wir verwenden **Redux Toolkit** für globales State Management:

```typescript
import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface UserState {
  currentUser: User | null;
  isAuthenticated: boolean;
}

const initialState: UserState = {
  currentUser: null,
  isAuthenticated: false,
};

export const userSlice = createSlice({
  name: 'user',
  initialState,
  reducers: {
    login: (state, action: PayloadAction<User>) => {
      state.currentUser = action.payload;
      state.isAuthenticated = true;
    },
    logout: (state) => {
      state.currentUser = null;
      state.isAuthenticated = false;
    },
  },
});
```

## 2.2 State-Hierarchie

```
Root State
├── user: UserState
├── products: ProductState
├── cart: CartState
└── ui: UIState
```

## 2.3 Performance-Optimierung

Memoization mit React.memo und useMemo:

- **React.memo**: Verhindert unnötige Re-Renders
- **useMemo**: Cached berechnete Werte
- **useCallback**: Cached Callback-Funktionen

## 2.4 Best Practices

1. ✅ Immutable State Updates (mit Immer)
2. ✅ Normalized State Shape
3. ✅ Action Creators mit TypeScript
4. ✅ Selektoren für komplexe Queries

## 2.5 Testing

Test-Coverage für State Management:

$$
\text{Coverage} = \frac{\text{Getestete Actions}}{\text{Gesamt Actions}} \times 100\% = 95\%
$$

🎯 Ziel: 100% Coverage für kritische Flows
