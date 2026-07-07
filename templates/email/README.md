# Email Marketing Templates

Email templates for every stage of the customer journey.

## Email Types

| Template | Stage | Goal |
|----------|-------|------|
| `welcome.md` | Onboarding | Welcome new subscribers, set expectations |
| `newsletter.md` | Nurture | Regular value delivery, stay top-of-mind |
| `promotional.md` | Conversion | Product offers, discounts, launches |
| `drip-campaign.md` | Nurture | Automated sequence over days/weeks |
| `re-engagement.md` | Win-back | Bring back inactive subscribers |
| `abandoned-cart.md` | Conversion | Recover lost sales |
| `announcement.md` | Awareness | Share news, updates, milestones |

## Structure

```markdown
---
type: [welcome/newsletter/promo/drip/re-engagement/cart/announce]
subject: "Subject line (under 50 chars)"
preheader: "Preview text (under 100 chars)"
tone: [professional/friendly/urgent]
---

## Subject Line
[Compelling subject — A/B test variations]

## Preheader
[Supportive preview text]

## Headline
[H1 - main message]

## Body
[Value-driven content, personalized]

## CTA
[One clear button/link]

## Footer
[Unsubscribe, address, social links]
```

## Best Practices

- **Subject line:** Under 50 characters, personalization, urgency or curiosity
- **Preheader:** Don't waste it — add supporting info
- **Personalization:** Use {{FIRST_NAME}}, {{COMPANY}} etc.
- **Mobile-first:** 70%+ opens are on mobile
- **One CTA:** One clear action per email
- **Testing:** Always A/B test subject lines
