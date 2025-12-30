# Component Stub List

## Components That Need to be Created with shadcn/ui

These components are referenced but need to be installed/created:

```bash
npx shadcn-ui@latest add button
npx shadcn-ui@latest add card
npx shadcn-ui@latest add dialog
npx shadcn-ui@latest add dropdown-menu
npx shadcn-ui@latest add input
npx shadcn-ui@latest add badge
npx shadcn-ui@latest add avatar
npx shadcn-ui@latest add skeleton
npx shadcn-ui@latest add separator
```

## Components Already Created

- ✅ `components/ui/label.tsx` - Created manually
- ✅ `components/ui/textarea.tsx` - Created manually
- ✅ `components/ui/select.tsx` - Created manually (with Radix UI)

## Missing Dependencies

You'll need to install these packages for the select component:

```bash
npm install @radix-ui/react-select @radix-ui/react-label
```

## Notes

- The `select.tsx` component uses Radix UI directly (as shadcn/ui does)
- The `label.tsx` component uses Radix UI Label
- All other UI components should be installed via shadcn/ui

