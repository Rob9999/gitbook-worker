# Kapitel 1: Component Library

## 1.1 Überblick

Unsere React Component Library bietet:

- **Buttons**: Primary, Secondary, Ghost
- **Forms**: Input, Select, Checkbox, Radio
- **Layout**: Container, Grid, Flex
- **Navigation**: Navbar, Sidebar, Breadcrumb

## 1.2 Beispiel: Button Component

```typescript
import React from 'react';

interface ButtonProps {
  variant: 'primary' | 'secondary' | 'ghost';
  onClick: () => void;
  children: React.ReactNode;
}

export const Button: React.FC<ButtonProps> = ({ 
  variant, 
  onClick, 
  children 
}) => {
  return (
    <button 
      className={`btn btn-${variant}`}
      onClick={onClick}
    >
      {children}
    </button>
  );
};
```

## 1.3 Component-Katalog

| Component | Variants | Status |
|-----------|----------|--------|
| Button | 3 | ✅ Stabil |
| Input | 5 | ✅ Stabil |
| Modal | 2 | 🚧 Beta |
| Toast | 4 | ✅ Stabil |

## 1.4 Accessibility

Alle Komponenten erfüllen **WCAG 2.1 Level AA** Standards:

- Keyboard-Navigation ⌨️
- Screen-Reader Support 🔊
- Color-Contrast-Ratio ≥ 4.5:1
